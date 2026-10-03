import asyncio

from workflow import run_workflow


async def main() -> None:
    user_description = input(
        "Describe your newsletter preferences: "
    )

    profile, search_plan, search_results, fetched_articles = await run_workflow(user_description)

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


if __name__ == "__main__":
    asyncio.run(main())
