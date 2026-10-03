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


class FetchedArticle(ArticleCandidate):
    content: str = Field(
        description="The main article text extracted from the source page."
    )


class NewsSearchResults(BaseModel):
    articles: list[ArticleCandidate] = Field(
        description=(
            "Unique, relevant article candidates found through web search. "
            "Return an empty list if no suitable articles are found."
        )
    )


class ArticleSummary(BaseModel):
    title: str = Field(
        description="The exact source article title."
    )

    url: str = Field(
        description="The exact source article URL."
    )

    published_date: str | None = Field(
        description="The supplied publication date, or null if unknown."
    )

    summary: str = Field(
        description=(
            "A concise, factual summary suited to the user's "
            "technical level and preferred tone."
        )
    )

    key_points: list[str] = Field(
        description="Two to three important points supported by the article."
    )


class NewsletterSection(BaseModel):
    heading: str = Field(
        description="A clear section heading suited to the user's interests."
    )

    body: str = Field(
        description=(
            "The section text, based on the supplied article summaries "
            "and suited to the user's technical level and preferred tone."
        )
    )

    source_urls: list[str] = Field(
        description=(
            "The exact URLs of supplied articles supporting this section."
        )
    )


class Newsletter(BaseModel):
    title: str = Field(
        description="A clear title for the personalized newsletter."
    )

    date: str = Field(
        description="The supplied current date in YYYY-MM-DD format."
    )

    introduction: str = Field(
        description="A brief introduction to the topics covered."
    )

    sections: list[NewsletterSection] = Field(
        description="Newsletter sections organized by topic."
    )


class SourceEvidence(BaseModel):
    url: str = Field(
        description="The exact URL of a supplied fetched article."
    )

    quote: str = Field(
        description="An exact excerpt from that article's content."
    )


class ClaimVerification(BaseModel):
    location: str = Field(
        description=(
            "The newsletter field containing the claim, "
            "such as introduction or sections[0].body."
        )
    )

    claim: str = Field(
        description="An exact excerpt from the newsletter containing a factual claim."
    )

    status: Literal[
        "supported",
        "unsupported",
        "contradicted",
        "not_a_claim",
    ] = Field(
        description=(
            "Whether an article-based factual claim is supported, "
            "unsupported, or contradicted; or whether the excerpt "
            "is an editorial label rather than a factual claim."
        )
    )

    evidence: list[SourceEvidence] = Field(
        description=(
            "Source excerpts used to assess the claim. "
            "Return an empty list when no relevant evidence is available."
        )
    )

    explanation: str = Field(
        description="A brief explanation of the verification result."
    )

    suggested_revision: str | None = Field(
        description=(
            "An evidence-backed replacement for a problematic claim. "
            "Return null if no correction is needed or the claim "
            "should be removed because no supported replacement exists."
        )
    )


class VerificationReport(BaseModel):
    checks: list[ClaimVerification] = Field(
        description=(
            "Checks covering every factual claim in the newsletter, "
            "including claims in its title, introduction, and sections."
        )
    )
