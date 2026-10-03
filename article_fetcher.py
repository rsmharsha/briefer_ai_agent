"""Download article candidates and extract their main text.

Requires httpx, trafilatura, and the project's existing schemas.py.
"""

import asyncio
import logging

import httpx
from trafilatura import extract

from schemas import ArticleCandidate, FetchedArticle

logger = logging.getLogger(__name__)


async def fetch_article(
    candidate: ArticleCandidate,
    client: httpx.AsyncClient,
) -> FetchedArticle | None:
    """Fetch one candidate; return None when downloading or extraction fails."""
    try:
        url = httpx.URL(candidate.url)

        if url.scheme not in {"http", "https"} or not url.host:
            raise ValueError("Expected an HTTP or HTTPS URL")

        response = await client.get(url)
        response.raise_for_status()

        content_type = (
            response.headers.get("content-type", "")
            .split(";")[0]
            .strip()
            .lower()
        )
        if content_type and content_type not in {
            "text/html",
            "application/xhtml+xml",
        }:
            raise ValueError(f"Unsupported content type: {content_type}")

    except (httpx.HTTPError, httpx.InvalidURL, ValueError) as error:
        logger.warning("Could not download %s: %s", candidate.url, error)
        return None

    try:
        # Run synchronous HTML extraction outside the async event loop.
        content = await asyncio.to_thread(
            extract,
            response.content,
            url=str(response.url),
            output_format="txt",
            include_comments=False,
            include_tables=True,
            favor_precision=True,
        )
    except Exception as error:
        logger.warning("Could not extract %s: %s", candidate.url, error)
        return None

    if not content or not content.strip():
        logger.warning("No usable article text found at %s", candidate.url)
        return None

    # Keep the candidate metadata and add the extracted source text.
    return FetchedArticle(
        **candidate.model_dump(),
        content=content.strip(),
    )


async def fetch_articles(
    candidates: list[ArticleCandidate],
) -> list[FetchedArticle]:
    """Fetch candidates in order and keep only successful extractions."""
    if not candidates:
        return []

    articles: list[FetchedArticle] = []

    # Reuse one HTTP client for the entire batch.
    async with httpx.AsyncClient(
        timeout=20.0,
        follow_redirects=True,
        max_redirects=5,
        headers={"User-Agent": "Briefer/0.1 (newsletter article fetcher)"},
    ) as client:
        for candidate in candidates:
            article = await fetch_article(candidate, client)

            if article is not None:
                articles.append(article)

    return articles

