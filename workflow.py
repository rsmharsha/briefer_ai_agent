from datetime import date

from agents import Runner

from agent_definitions import user_profiler_agent, planner_agent
from schemas import UserProfile, SearchPlan


async def run_workflow(
    user_description: str,
) -> tuple[UserProfile, SearchPlan]:

    # Run the profiler.
    profiler_result = await Runner.run(
        user_profiler_agent,
        input=user_description,
    )

    profile: UserProfile = profiler_result.final_output

    # Prepare the planner's input.
    today = date.today().isoformat()

    planner_input = (
        f"Current date: {today}\n\n"
        f"User profile:\n{profile.model_dump_json()}"
    )

    # Run the planner.
    planner_result = await Runner.run(
        planner_agent,
        input=planner_input,
    )

    search_plan: SearchPlan = planner_result.final_output

    return profile, search_plan