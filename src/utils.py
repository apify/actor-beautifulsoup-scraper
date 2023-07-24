import re
from inspect import iscoroutinefunction
from typing import Callable, cast
from urllib.parse import urljoin

from apify import Actor
from apify.storages import RequestQueue
from bs4 import BeautifulSoup

from .dataclasses import Context

USER_DEFINED_FUNCTION_NAME = 'page_function'


async def get_proxies_from_conf(proxy_configuration: dict | None) -> dict | None:
    """Retrieves the proxies dictionary based on the provided proxy configuration.

    Args:
        proxy_configuration: The proxy configuration dictionary. If None, no proxies will be used.

    Returns:
        The proxies dictionary containing "http" and "https" keys with the proxy URL.
        Returns None if proxy_configuration is None.
    """
    if proxy_configuration:
        conf = await Actor.create_proxy_configuration(actor_proxy_input=proxy_configuration)

        if conf is None:
            Actor.log.error('Creation of proxy configuration failed, exiting...')
            await Actor.exit(exit_code=1)
        else:
            proxy_url = await conf.new_url()
            return {'http://': proxy_url, 'https://': proxy_url}

    return None


async def update_request_queue(
    soup: BeautifulSoup,
    request_queue: RequestQueue,
    request: dict,
    max_depth: int,
    link_selector: str,
    link_patterns: list[str],
) -> None:
    """Updates the request queue with new links found in the response.

    This function parses the HTML content of the response using BeautifulSoup and extracts links based
    on the provided CSS selector. It then checks each link against the specified regex patterns to determine
    if it should be enqueued in the request queue. The depth of the links is compared to the maximum depth
    to avoid exceeding it. Valid links are enqueued with an increased depth in the request queue.

    Args:
        soup: The BeautifulSoup object to get links from.
        request_queue: The request queue to update.
        request: The original request.
        max_depth: The maximum depth allowed for enqueueing links.
        link_selector: The CSS selector to locate the links in the HTML content.
        link_patterns: The list of regex patterns to match the links against.

    Returns:
        None
    """
    url = request['url']
    depth = request['userData']['depth']

    if depth >= max_depth:
        return

    items = soup.select(link_selector)

    # If we haven't reached the max depth, look for nested links and enqueue their targets
    for item in items:
        link_url = urljoin(url, item['href'])

        # Regex matching
        matched = False
        for pattern in link_patterns:
            if re.match(pattern, link_url):
                matched = True
                break

        if not matched:
            Actor.log.debug(f'Link URL {link_url} does not match any pattern')
            continue

        if not link_url.startswith(('http://', 'https://')):
            Actor.log.debug(f'Link URL {link_url} does not start with http/https')
            continue

        Actor.log.info(f'Enqueuing {link_url} ...')
        await request_queue.add_request(request={'url': link_url, 'userData': {'depth': depth + 1}})


async def extract_user_function(page_function: str) -> Callable:
    """Extracts the user-defined function using exec and returns it as a Callable.

    This function uses `exec` internally to execute the `page_function` code in a separate scope. The `page_function`
    should be a valid Python code snippet defining a function named `USER_DEFINED_FUNCTION_NAME`.

    Args:
        page_function: The string representation of the user-defined function.

    Returns:
        The extracted user-defined function.

    Raises:
        KeyError: If the function name `USER_DEFINED_FUNCTION_NAME` cannot be found.
    """
    scope: dict = {'Context': Context}
    exec(page_function, scope)

    try:
        user_defined_function = scope[USER_DEFINED_FUNCTION_NAME]
    except KeyError:
        Actor.log.error(f'Function name "{USER_DEFINED_FUNCTION_NAME}" could not be found, exiting...')
        await Actor.exit(exit_code=1)

    return cast(Callable, user_defined_function)


async def execute_user_function(context: Context, user_defined_function: Callable) -> None:
    """Executes the user-defined function with the provided context and pushes data to the Actor.

    This function checks if the provided user-defined function is a coroutine. If it is, the function is awaited.
    If it is not, it is executed directly.

    Args:
        context: The context object to be passed as an argument to the function.
        user_defined_function: The user-defined function to be executed.

    Returns:
        None
    """
    if iscoroutinefunction(user_defined_function):
        result = await user_defined_function(context)
    else:
        result = user_defined_function(context)

    await Actor.push_data(result)
