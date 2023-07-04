import re
from inspect import iscoroutinefunction
from typing import Callable, NamedTuple
from urllib.parse import urljoin

import requests
from apify import Actor
from apify.storages import RequestQueue
from bs4 import BeautifulSoup

DEFAULT_MAX_DEPTH = float("inf")  # unlimited
DEFAULT_LINK_PATTERNS = ".*"  # matches everything
DEFAULT_REQUESTS_TIMEOUT = 10
USER_DEFINED_FUNCTION_NAME = "page_function"


class Context(NamedTuple):
    """
    Instance of the Context class is provided to the user-defined function.
    """

    request: dict
    response: requests.Response
    request_queue: RequestQueue


async def get_proxies_for_requests(proxy_configuration: dict | None) -> dict | None:
    """
    Get proxies dictionary based on the proxy configuration.
    """
    if proxy_configuration:
        conf = await Actor.create_proxy_configuration(actor_proxy_input=proxy_configuration)

        if conf is None:
            Actor.log.error("Creation of proxy configuration failed, exiting...")
            await Actor.exit(exit_code=1)
        else:
            proxy_url = await conf.new_url()
            return {"http": proxy_url, "https": proxy_url}

    return None


async def update_request_queue(
    request_queue: RequestQueue,
    request: dict,
    response: requests.Response,
    max_depth: int,
    link_selector: str,
    link_patterns: list[str],
) -> None:
    """
    Update the request queue with the new links found in the response.
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
            Actor.log.debug(f"Link URL ({link_url}) does not match any pattern")
            continue

        if not link_url.startswith(("http://", "https://")):
            Actor.log.debug(f"Link URL ({link_url}) does not start with http/https")
            continue

        Actor.log.info(f"Enqueuing {link_url} ...")
        await request_queue.add_request(request={"url": link_url, "userData": {"depth": depth + 1}})


async def extract_user_defined_function(page_function: str) -> Callable:
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


async def execute_user_defined_function(context: Context, user_defined_function: Callable) -> None:
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
        # Read the Actor input
        actor_input = await Actor.get_input() or {}
        start_urls: list[dict] = actor_input.get("startUrls", [])
        link_selector = actor_input.get("linkSelector")
        link_patterns = actor_input.get("linkPatterns", DEFAULT_LINK_PATTERNS)
        page_function = actor_input.get("pageFunction")
        max_depth = actor_input.get("maxDepth", DEFAULT_MAX_DEPTH)
        proxy_configuration = actor_input.get("proxyConfiguration")

        Actor.log.debug(f"start_urls = {start_urls}")
        Actor.log.debug(f"link_selector = {link_selector}")
        Actor.log.debug(f"link_patterns = {link_patterns}")
        Actor.log.debug(f"page_function = {page_function}")
        Actor.log.debug(f"max_depth = {max_depth}")
        Actor.log.debug(f"proxy_configuration = {proxy_configuration}")

        if not start_urls:
            Actor.log.info("No start URLs specified in actor input, exiting...")
            await Actor.exit()

        # Enqueue the starting URLs in the default request queue
        request_queue = await Actor.open_request_queue()
        for start_url in start_urls:
            url = start_url.get("url")
            Actor.log.info(f"Enqueuing {url} ...")
            await request_queue.add_request(request={"url": url, "userData": {"depth": 0}})

        proxies = await get_proxies_for_requests(proxy_configuration)
        user_defined_function = await extract_user_defined_function(page_function)

        # Process the requests in the queue one by one
        while request := await request_queue.fetch_next_request():
            url = request["url"]
            Actor.log.info(f"Scraping {url} ...")

            try:
                response = requests.get(url, proxies=proxies, timeout=DEFAULT_REQUESTS_TIMEOUT)
                context = Context(request, response, request_queue)

                if link_selector:
                    await update_request_queue(
                        request_queue, request, response, max_depth, link_selector, link_patterns
                    )

                if page_function:
                    await execute_user_defined_function(context, user_defined_function)

            finally:
                # Mark the request as handled so it's not processed again
                await request_queue.mark_request_as_handled(request)
