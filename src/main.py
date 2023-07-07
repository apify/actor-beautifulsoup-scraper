import re
from inspect import iscoroutinefunction
from typing import Callable
from urllib.parse import urljoin

from apify import Actor
from apify.storages import RequestQueue
from bs4 import BeautifulSoup
from httpx import AsyncClient, Response

from .dataclasses import ActorInputData, Context

USER_DEFINED_FUNCTION_NAME = "page_function"


async def _get_proxies_from_conf(proxy_configuration: dict | None) -> dict | None:
    """
    Retrieves the proxies dictionary based on the provided proxy configuration.

    Args:
        proxy_configuration: The proxy configuration dictionary. If None, no proxies will be used.

    Returns:
        The proxies dictionary containing "http" and "https" keys with the proxy URL.
        Returns None if proxy_configuration is None.
    """
    if proxy_configuration:
        conf = await Actor.create_proxy_configuration(actor_proxy_input=proxy_configuration)

        if conf is None:
            Actor.log.error("Creation of proxy configuration failed, exiting...")
            await Actor.exit(exit_code=1)
        else:
            proxy_url = await conf.new_url()
            return {"http://": proxy_url, "https://": proxy_url}

    return None


async def _update_request_queue(
    request_queue: RequestQueue,
    request: dict,
    response: Response,
    max_depth: int,
    link_selector: str,
    link_patterns: list[str],
) -> None:
    """
    Updates the request queue with new links found in the response.

    This function parses the HTML content of the response using BeautifulSoup and extracts links based
    on the provided CSS selector. It then checks each link against the specified regex patterns to determine
    if it should be enqueued in the request queue. The depth of the links is compared to the maximum depth
    to avoid exceeding it. Valid links are enqueued with an increased depth in the request queue.

    Args:
        request_queue: The request queue to update.
        request: The original request.
        response: The response object containing the HTML content.
        max_depth: The maximum depth allowed for enqueueing links.
        link_selector: The CSS selector to locate the links in the HTML content.
        link_patterns: The list of regex patterns to match the links against.

    Returns:
        None
    """
    soup = BeautifulSoup(response.content, "html.parser")
    url = request["url"]
    depth = request["userData"]["depth"]

    if depth >= max_depth:
        return

    items = soup.select(link_selector)

    # If we haven't reached the max depth, look for nested links and enqueue their targets
    for item in items:
        link_url = urljoin(url, item["href"])

        # Regex matching
        matched = False
        for pattern in link_patterns:
            if re.match(pattern, link_url):
                matched = True
                break

        if not matched:
            Actor.log.debug(f"Link URL {link_url} does not match any pattern")
            continue

        if not link_url.startswith(("http://", "https://")):
            Actor.log.debug(f"Link URL {link_url} does not start with http/https")
            continue

        Actor.log.info(f"Enqueuing {link_url} ...")
        await request_queue.add_request(request={"url": link_url, "userData": {"depth": depth + 1}})


async def _extract_user_defined_function(page_function: str) -> Callable:
    """
    Extracts the user-defined function using exec and returns it as a Callable.

    This function uses `exec` internally to execute the `page_function` code in a separate scope. The `page_function`
    should be a valid Python code snippet defining a function named `USER_DEFINED_FUNCTION_NAME`.

    Args:
        page_function: The string representation of the user-defined function.

    Returns:
        The extracted user-defined function.

    Raises:
        KeyError: If the function name `USER_DEFINED_FUNCTION_NAME` cannot be found.
    """
    scope: dict = {"Context": Context}
    exec(page_function, scope)  # pylint: disable=exec-used

    try:
        user_defined_function = scope[USER_DEFINED_FUNCTION_NAME]
    except KeyError:
        Actor.log.error(f'Function name "{USER_DEFINED_FUNCTION_NAME}" could not be find, exiting...')
        await Actor.exit(exit_code=1)

    return user_defined_function


async def _execute_user_defined_function(context: Context, user_defined_function: Callable) -> None:
    """
    Executes the user-defined function with the provided context.

    This function checks if the provided user-defined function is a coroutine. If it is, the function is awaited.
    If it is not, it is executed directly.

    Args:
        context: The context object to be passed as an argument to the function.
        user_defined_function: The user-defined function to be executed.

    Returns:
        None
    """
    if iscoroutinefunction(user_defined_function):
        await user_defined_function(context)
    else:
        user_defined_function(context)


async def main():
    async with Actor:
        aid = await ActorInputData.from_input()

        # Enqueue the starting URLs in the default request queue
        request_queue = await Actor.open_request_queue()
        for start_url in aid.start_urls:
            url = start_url.get("url")
            Actor.log.info(f"Enqueuing {url} ...")
            await request_queue.add_request(request={"url": url, "userData": {"depth": 0}})

        user_defined_function = await _extract_user_defined_function(aid.page_function)
        proxies = await _get_proxies_from_conf(aid.proxy_configuration)

        # Process the requests in the queue one by one
        while request := await request_queue.fetch_next_request():
            url = request["url"]
            Actor.log.info(f"Scraping {url} ...")

            try:
                async with AsyncClient(proxies=proxies) as client:
                    response = await client.get(url, timeout=aid.request_timeout)

                context = Context(request, response, request_queue)

                if aid.link_selector:
                    await _update_request_queue(
                        request_queue, request, response, aid.max_depth, aid.link_selector, aid.link_patterns
                    )

                await _execute_user_defined_function(context, user_defined_function)

            except:  # pylint: disable=bare-except
                Actor.log.exception(f"Cannot extract data from {url}.")

            finally:
                # Mark the request as handled so it's not processed again
                await request_queue.mark_request_as_handled(request)
