"""Bounded verification and revision for Briefer's newsletter drafts."""

import json
import re
from typing import Literal

from agents import Runner
from pydantic import BaseModel

from agent_definitions import newsletter_revision_agent, verification_agent
from schemas import FetchedArticle, Newsletter, UserProfile, VerificationReport
from verification_utils import normalize_whitespace, validate_evidence


MAX_REVISIONS = 2
MAX_VERIFICATION_ATTEMPTS = 2


class NewsletterReviewResult(BaseModel):
    """Created by Python to describe the latest draft and its review."""

    newsletter: Newsletter
    verification_report: VerificationReport
    status: Literal["passed_checks", "needs_review"]
    revisions_used: int
    validation_errors: list[str]


def _draft_errors(
    draft: Newsletter,
    articles: list[FetchedArticle],
    current_date: str,
    max_words: int,
) -> list[str]:
    errors: list[str] = []
    allowed_urls = {article.url for article in articles}
    text = "\n".join(
        [draft.introduction] + [section.body for section in draft.sections]
    )
    word_count = len(text.split())

    if draft.date != current_date:
        errors.append(f"Set the newsletter date to {current_date}.")
    if word_count > max_words:
        errors.append(
            f"The introduction and section bodies contain {word_count} words; "
            f"shorten them to at most {max_words}."
        )
    if not draft.title.strip():
        errors.append("Provide a newsletter title.")
    if not draft.sections:
        errors.append("The newsletter has no sections with supported content.")

    for index, section in enumerate(draft.sections):
        if not section.body.strip():
            errors.append(f"Remove or complete empty section {index}.")
        if not section.source_urls:
            errors.append(f"Section {index} needs supporting source URLs.")
        for url in section.source_urls:
            if url not in allowed_urls:
                errors.append(
                    f"Section {index} cites an article that was not fetched: {url}"
                )

    return errors


def _report_errors(
    report: VerificationReport,
    draft: Newsletter,
    articles: list[FetchedArticle],
) -> list[str]:
    errors = validate_evidence(report, articles)
    checked_sections: set[int] = set()

    for index, check in enumerate(report.checks, start=1):
        label = f"Check {index} ({check.location})"
        section_index: int | None = None

        if check.location in {"title", "introduction"}:
            field_text = getattr(draft, check.location)
        else:
            match = re.fullmatch(r"sections\[(\d+)\]\.(heading|body)", check.location)
            if match is None or int(match.group(1)) >= len(draft.sections):
                errors.append(f"{label}: use a valid newsletter field location.")
                continue
            section_index = int(match.group(1))
            field_name = match.group(2)
            field_text = getattr(draft.sections[section_index], field_name)
            if field_name == "body" and check.status != "not_a_claim":
                checked_sections.add(section_index)

        claim = normalize_whitespace(check.claim)
        if not claim or claim not in normalize_whitespace(field_text):
            errors.append(f"{label}: copy the claim from the current draft exactly.")

        if check.status == "not_a_claim":
            if check.evidence or check.suggested_revision is not None:
                errors.append(
                    f"{label}: not_a_claim needs empty evidence and a null revision."
                )
        elif check.status == "supported":
            if check.suggested_revision is not None:
                errors.append(f"{label}: supported claims need a null revision.")
            if section_index is not None:
                cited_urls = set(draft.sections[section_index].source_urls)
                if any(evidence.url not in cited_urls for evidence in check.evidence):
                    errors.append(
                        f"{label}: assess support using the section's cited articles; "
                        "report a missing citation as unsupported."
                    )

    for index, section in enumerate(draft.sections):
        if section.body.strip() and index not in checked_sections:
            errors.append(f"No factual checks were returned for sections[{index}].body.")

    return errors


async def review_newsletter(
    newsletter: Newsletter,
    profile: UserProfile,
    fetched_articles: list[FetchedArticle],
    current_date: str,
) -> NewsletterReviewResult:
    """Verify every draft, retry invalid reports, and allow up to two revisions.

    passed_checks means the returned report and Python checks passed. The
    verifier still judges claim support; these checks do not establish that
    every possible factual claim was identified or independently confirmed.
    """
    max_words = {"short": 250, "medium": 450, "long": 700}.get(
        profile.preferred_length, 450
    )
    articles = [
        {
            "title": article.title,
            "url": article.url,
            "published_date": article.published_date,
            "content": article.content,
        }
        for article in fetched_articles
    ]
    draft = newsletter

    for revisions_used in range(MAX_REVISIONS + 1):
        report: VerificationReport | None = None
        report_errors: list[str] = []

        # Retry the verifier, without rewriting the draft, if its report is invalid.
        for _ in range(MAX_VERIFICATION_ATTEMPTS):
            result = await Runner.run(
                verification_agent,
                input=json.dumps(
                    {
                        "task": "Verify this draft and correct any validation_feedback.",
                        "current_date": current_date,
                        "newsletter": draft.model_dump(),
                        "fetched_articles": articles,
                        "validation_feedback": report_errors,
                        "previous_verification_report": (
                            report.model_dump() if report is not None else None
                        ),
                    },
                    ensure_ascii=False,
                ),
            )
            report = result.final_output
            report_errors = _report_errors(report, draft, fetched_articles)
            if not report_errors:
                break

        if report is None:
            raise RuntimeError("The verifier returned no report.")

        draft_errors = _draft_errors(draft, fetched_articles, current_date, max_words)
        flagged_checks = [
            check
            for check in report.checks
            if check.status in {"unsupported", "contradicted"}
        ]

        def outcome(status: Literal["passed_checks", "needs_review"]):
            return NewsletterReviewResult(
                newsletter=draft,
                verification_report=report,
                status=status,
                revisions_used=revisions_used,
                validation_errors=report_errors + draft_errors,
            )

        # An invalid report cannot approve a draft or guide automatic revisions.
        if report_errors:
            return outcome("needs_review")
        if not flagged_checks and not draft_errors:
            return outcome("passed_checks")
        if revisions_used == MAX_REVISIONS:
            return outcome("needs_review")

        revision_result = await Runner.run(
            newsletter_revision_agent,
            input=json.dumps(
                {
                    "user_profile": profile.model_dump(),
                    "current_date": current_date,
                    "newsletter": draft.model_dump(),
                    "verification_report": report.model_dump(),
                    "fetched_articles": articles,
                    "max_words": max_words,
                    "revision_feedback": draft_errors,
                },
                ensure_ascii=False,
            ),
        )
        draft = revision_result.final_output

    raise RuntimeError("The review loop ended without a result.")
