from typing import Literal
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    interests: list[str]
    technical_level: Literal[
        "beginner", "intermediate", "advanced", "unknown"
    ]
    preferred_tone: Literal[
        "simple", "technical", "casual", "formal", "unknown"
    ]
    preferred_length: Literal[
        "short", "medium", "long", "unknown"
    ]


class SearchPlan(BaseModel):
    search_queries: list[str] = Field(
        description=(
            "Specific search queries based on the user's interests "
            "and technical level."
        )
    )

    preferred_source_types: list[str] = Field(
        description=(
            "Preferred source categories, such as official announcements, "
            "official documentation, research papers, or educational articles."
        )
    )

    max_articles: int = Field(
        description=(
            "Maximum number of articles to include: "
            "3 for short, 5 for medium or unknown, and 7 for long newsletters."
        )
    )

    section_titles: list[str] = Field(
        description="Newsletter section titles suited to the user's interests."
    )


class ArticleCandidate(BaseModel):
    title: str = Field(
        description="The article title found in the search results."
    )

    url: str = Field(
        description="The source URL for the article."
    )

    snippet: str = Field(
        description="A brief preview based on the search results."
    )

    published_date: str | None = Field(
        description=(
            "Publication date in YYYY-MM-DD format when provided "
            "by the source. Otherwise, null. Do not guess."
        )
    )


class NewsSearchResults(BaseModel):
    articles: list[ArticleCandidate] = Field(
        description=(
            "Unique, relevant article candidates found through web search. "
            "Return an empty list if no suitable articles are found."
        )
    )