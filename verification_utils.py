from schemas import FetchedArticle, VerificationReport


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def validate_evidence(
    report: VerificationReport,
    articles: list[FetchedArticle],
) -> list[str]:
    errors: list[str] = []

    if not report.checks:
        return ["The verifier returned no checks."]

    content_by_url = {
        article.url: normalize_whitespace(article.content)
        for article in articles
    }

    for index, check in enumerate(report.checks, start=1):
        label = f"Check {index} ({check.location})"

        if (
            check.status in {"supported", "contradicted"}
            and not check.evidence
        ):
            errors.append(f"{label}: source evidence is missing.")

        for evidence in check.evidence:
            source_text = content_by_url.get(evidence.url)
            quote = normalize_whitespace(evidence.quote)

            if source_text is None:
                errors.append(
                    f"{label}: evidence URL was not fetched."
                )
            elif not quote:
                errors.append(f"{label}: evidence quote is empty.")
            elif quote not in source_text:
                errors.append(
                    f"{label}: quote does not match the source text."
                )

    return errors
