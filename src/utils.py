from __future__ import annotations

from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Callable

from apify import Actor

if TYPE_CHECKING:
    from crawlee.beautifulsoup_crawler import BeautifulSoupCrawlingContext

USER_DEFINED_FUNCTION_NAME = 'page_function'


async def execute_user_function(context: BeautifulSoupCrawlingContext, user_defined_function: Callable) -> None:
    """Execute the user-defined function with the provided context and pushes data to the Actor.

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
