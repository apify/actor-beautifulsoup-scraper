from apify import Actor
from bs4 import BeautifulSoup
from httpx import AsyncClient

from .dataclasses import ActorInputData, Context
from .utils import execute_user_function, extract_user_function, get_proxies_from_conf, update_request_queue


async def main() -> None:
    """Actor main function."""
    async with Actor:
        aid = await ActorInputData.from_input()

        # Enqueue the starting URLs in the default request queue
        request_queue = await Actor.open_request_queue()
        for start_url in aid.start_urls:
            url = start_url.get('url')
            Actor.log.info(f'Enqueuing {url} ...')
            await request_queue.add_request(request={'url': url, 'userData': {'depth': 0}})

        user_defined_function = await extract_user_function(aid.page_function)
        proxies = await get_proxies_from_conf(aid.proxy_configuration)

        # Process the requests in the queue one by one
        while request := await request_queue.fetch_next_request():
            url = request['url']
            Actor.log.info(f'Scraping {url} ...')

            try:
                # Todo: Think about using the same client for the whole request queue. It was discussed here -
                # https://github.com/apify/actor-beautifulsoup-scraper/pull/1#pullrequestreview-1518377074.
                async with AsyncClient(proxies=proxies) as client:
                    response = await client.get(url, timeout=aid.request_timeout)

                soup = BeautifulSoup(
                    response.content,
                    features=aid.soup_features,
                    from_encoding=aid.soup_from_encoding,
                    exclude_encodings=aid.soup_exclude_encodings,
                )

                if aid.link_selector:
                    await update_request_queue(
                        soup,
                        request_queue,
                        request,
                        aid.max_depth,
                        aid.link_selector,
                        aid.link_patterns,
                    )

                context = Context(soup, request, request_queue, response)
                await execute_user_function(context, user_defined_function)

            except BaseException:
                Actor.log.exception(f'Cannot extract data from {url}.')

            finally:
                # Mark the request as handled so it's not processed again
                await request_queue.mark_request_as_handled(request)
