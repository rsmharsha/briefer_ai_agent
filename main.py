import asyncio

from workflow import run_workflow


async def main() -> None:
    user_description = input(
        "Describe your newsletter preferences: "
    )

    profile, search_plan, search_results = await run_workflow(user_description)

    print("\nUSER PROFILE:")
    print(profile.model_dump_json(indent=2))

    print("\nSEARCH PLAN:")
    print(search_plan.model_dump_json(indent=2))

    print("\nARTICLE CANDIDATES:")
    print(search_results.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
