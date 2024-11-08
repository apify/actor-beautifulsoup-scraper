from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

from apify import Actor

from .input_handling import ActorInputData
from .utils import execute_user_function


async def main() -> None:
    """Actor main function."""
    async with Actor:
        aid = await ActorInputData.from_input()

        crawler = BeautifulSoupCrawler(
            parser=aid.soup_features,
            max_crawl_depth=aid.max_depth,
            proxy_configuration=aid.proxy_configuration,
            request_handler_timeout=aid.request_timeout,
        )

        @crawler.router.default_handler
        async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
            # Process the request.
            Actor.log.info(f'Scraping {context.request.url} ...')
            await execute_user_function(context, aid.user_function)

            if aid.link_selector:
                await context.enqueue_links(selector=aid.link_selector, include=aid.link_patterns)

        await crawler.run(aid.start_urls)
