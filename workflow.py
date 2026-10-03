from datetime import date

from agents import Runner

from agent_definitions import (
    user_profiler_agent,
    planner_agent,
    news_search_agent,
)
from article_fetcher import fetch_articles
from schemas import (
    UserProfile,
    SearchPlan,
    NewsSearchResults,
    FetchedArticle,
)


async def run_workflow(
    user_description: str,
) -> tuple[UserProfile, SearchPlan, NewsSearchResults, list[FetchedArticle]]:

    # 1. Create the user profile.
    profiler_result = await Runner.run(
        user_profiler_agent,
        input=user_description,
    )

    profile: UserProfile = profiler_result.final_output

    # 2. Create the search plan.
    today = date.today().isoformat()

    planner_input = (
        f"Current date: {today}\n\n"
        f"User profile:\n{profile.model_dump_json()}"
    )

    planner_result = await Runner.run(
        planner_agent,
        input=planner_input,
    )

    search_plan: SearchPlan = planner_result.final_output

    # 3. Search for article candidates.
    search_results = NewsSearchResults(articles=[])

    if search_plan.search_queries and search_plan.max_articles > 0:
        search_input = (
            f"Current date: {today}\n\n"
            f"Search plan:\n{search_plan.model_dump_json()}"
        )

        search_result = await Runner.run(
            news_search_agent,
            input=search_input,
        )

        search_results = search_result.final_output

    # 4. Download and extract the article text.
    fetched_articles = await fetch_articles(search_results.articles)

    return profile, search_plan, search_results, fetched_articles