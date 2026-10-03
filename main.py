import asyncio
from workflow import run_workflow
from verification_utils import validate_evidence


async def main() -> None:
    user_description = input(
        "Describe your newsletter preferences: "
    )

    profile, search_plan, search_results, fetched_articles, article_summaries, newsletter, verification_report = await run_workflow(user_description)

    print("\nUSER PROFILE:")
    print(profile.model_dump_json(indent=2))

    print("\nSEARCH PLAN:")
    print(search_plan.model_dump_json(indent=2))

    print("\nARTICLE CANDIDATES:")
    print(search_results.model_dump_json(indent=2))

    print(
        f"\nFETCHED ARTICLES: "
        f"{len(fetched_articles)} / {len(search_results.articles)}"
    )

    if not fetched_articles:
        print("No usable article text could be fetched.")

    for article in fetched_articles:
        print(f"\nTitle: {article.title}")
        print(f"URL: {article.url}")
        print(f"Characters extracted: {len(article.content)}")
        print(f"Preview:\n{article.content[:500]}")

    print(f"\nARTICLE SUMMARIES: {len(article_summaries)}")
    for article_summary in article_summaries:
        print(article_summary.model_dump_json(indent=2))

    print("\nNEWSLETTER DRAFT:")

    if newsletter is None:
        print("No usable article summaries were available.")
    else:
        print(newsletter.model_dump_json(indent=2))

    print("\nVERIFICATION REPORT:")

    if verification_report is None:
        print("No newsletter draft was available to verify.")
    else:
        print(verification_report.model_dump_json(indent=2))

        flagged_count = sum(
            check.status in {"unsupported", "contradicted"}
            for check in verification_report.checks
        )

        print(f"\nClaims checked: {len(verification_report.checks)}")
        print(f"Claims flagged: {flagged_count}")

        # Add the evidence validation here.
        evidence_errors = validate_evidence(
            verification_report,
            fetched_articles,
        )

        if evidence_errors:
            print("\nEVIDENCE VALIDATION ERRORS:")
            for error in evidence_errors:
                print(f"- {error}")
        else:
            print("\nEvidence quotes match the fetched source text.")


if __name__ == "__main__":
    asyncio.run(main())
