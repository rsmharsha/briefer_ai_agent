"""Render and save Briefer newsletters that passed review."""

from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from newsletter_review import NewsletterReviewResult
from schemas import Newsletter


def newsletter_to_markdown(newsletter: Newsletter) -> str:
    """Format a newsletter with headings, paragraphs, and source links."""
    lines = [
        f"# {newsletter.title.strip()}",
        "",
        f"**Date:** {newsletter.date}",
        "",
        newsletter.introduction.strip(),
        "",
    ]

    for section in newsletter.sections:
        lines.extend([
            f"## {section.heading.strip()}",
            "",
            section.body.strip(),
            "",
            "**Sources:**",
            "",
        ])
        for url in dict.fromkeys(section.source_urls):
            lines.append(f"- <{url}>")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def save_newsletter(
    review_result: NewsletterReviewResult,
    output_dir: str | Path | None = None,
) -> Path:
    """Save the latest reviewed draft and return the Markdown file path.

    By default, files go in outputs/ beside this module. Each export has a
    distinct filename, and exclusive creation prevents overwriting a file.
    """
    if review_result.status != "passed_checks":
        raise ValueError("Only newsletters that passed review can be exported.")

    newsletter = review_result.newsletter
    issue_date = date.fromisoformat(newsletter.date).isoformat()
    markdown = newsletter_to_markdown(newsletter)
    directory = (
        Path(output_dir)
        if output_dir is not None
        else Path(__file__).resolve().parent / "outputs"
    )
    directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    filename = f"newsletter_{issue_date}_{timestamp}_{uuid4().hex[:8]}.md"
    output_path = directory / filename

    with output_path.open("x", encoding="utf-8", newline="\n") as file:
        file.write(markdown)

    return output_path
