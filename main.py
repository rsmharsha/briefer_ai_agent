import asyncio
from workflow import run_workflow
from newsletter_export import save_newsletter


async def main() -> None:
    user_description = input(
        "Describe your newsletter preferences: "
    )

    profile, search_plan, search_results, fetched_articles, article_summaries, newsletter, review_result, = await run_workflow(user_description)

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

    print("\nNEWSLETTER REVIEW:")

    if review_result is None:
        print("No newsletter was available to review.")
    else:
        print(f"Status: {review_result.status}")
        print(f"Revisions used: {review_result.revisions_used}")

        print("\nVERIFICATION REPORT:")
        print(
            review_result.verification_report.model_dump_json(indent=2)
        )

        if review_result.validation_errors:
            print("\nVALIDATION ERRORS:")
            for error in review_result.validation_errors:
                print(f"- {error}")

    
    if review_result is not None:
        if review_result.status == "passed_checks":
            try:
                saved_path = save_newsletter(review_result)
            except (OSError, ValueError) as error:
                print(f"\nCould not save newsletter: {error}")
            else:
                print(f"\nNewsletter saved to: {saved_path.resolve()}")
        else:
            print("\nNewsletter needs review; export skipped.")


if __name__ == "__main__":
    asyncio.run(main())
