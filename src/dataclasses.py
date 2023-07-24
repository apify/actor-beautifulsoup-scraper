from dataclasses import dataclass
from typing import Any

from apify import Actor
from apify.storages import RequestQueue
from bs4 import BeautifulSoup
from httpx import Response


@dataclass(frozen=True)
class ActorInputData:
    """
    Immutable data class representing the input data for the Actor.
    """

    start_urls: list[dict]
    link_selector: str | None
    link_patterns: list[str]
    max_depth: int
    request_timeout: int
    proxy_configuration: Any
    soup_features: str | None
    soup_from_encoding: str | None
    soup_exclude_encodings: str | None
    page_function: str | None

    @classmethod
    async def from_input(cls) -> 'ActorInputData':
        actor_input = await Actor.get_input() or {}

        aid = cls(
            actor_input.get('startUrls', []),
            actor_input.get('linkSelector'),
            actor_input.get('linkPatterns', ['.*']),  # default matches everything
            actor_input.get('maxCrawlingDepth', 1),  # default is 1
            actor_input.get('requestTimeout', 10),  # default is 10
            actor_input.get('proxyConfiguration'),
            actor_input.get('soupFeatures', 'html.parser'),  # default is "html.parser"
            actor_input.get('soupFromEncoding'),
            actor_input.get('soupExcludeEncodings'),
            actor_input.get('pageFunction'),
        )

        Actor.log.debug(f'actor_input = {aid}')

        if not aid.start_urls:
            Actor.log.error('No start URLs specified in actor input, exiting...')
            await Actor.exit(exit_code=1)

        if not aid.page_function:
            Actor.log.error('No page function specified in actor input, exiting...')
            await Actor.exit(exit_code=1)

        return aid


@dataclass(frozen=True)
class Context:
    """
    Immutable data class representing the context argument provided to the user-defined function.
    """

    soup: BeautifulSoup
    request: dict
    request_queue: RequestQueue
    response: Response
