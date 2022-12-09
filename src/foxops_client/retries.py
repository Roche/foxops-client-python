import functools

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_delay,
    wait_random_exponential,
)

HTTP_RETRYABLE_STATUS_CODES = (
    httpx.codes.REQUEST_TIMEOUT,
    httpx.codes.BAD_GATEWAY,
    httpx.codes.SERVICE_UNAVAILABLE,
    httpx.codes.GATEWAY_TIMEOUT,
)


def retryable_exception(e: BaseException) -> bool:
    if not isinstance(e, httpx.HTTPStatusError):
        return False

    if e.response.status_code in HTTP_RETRYABLE_STATUS_CODES:
        return True

    return False


default_retry = functools.partial(
    retry,
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_delay(5 * 60),
    retry=retry_if_exception(retryable_exception),
)
