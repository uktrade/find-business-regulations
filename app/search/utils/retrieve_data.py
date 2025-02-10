import logging

from typing import Optional

import requests  # type: ignore

logger = logging.getLogger(__name__)


def get_data_from_url(
    config, url, type: str = "public", params: Optional[dict] = None
):
    """
    Fetch data from a given URL and return the response text if successful,
    otherwise log the error.

    Parameters:
    - config: Configuration object that includes the request timeout.
    - url: String representing the URL to request.

    Returns:
    - Response text if the status code is 200.
    - None if the response status code is not 200, or if there is an exception
        during the request.

    Logs:
    - Error messages for request failures and non-200 response codes.
    """
    try:
        response = requests.get(
            url,
            timeout=config.timeout,
            **({"params": params} if params else {}),
        )  # nosec BXXX

        if response.status_code == 200:
            return response.text

        # If the status code is not 200, log the error
        logger.error(
            f"error fetching data {type} from {url}: "
            f"[{response.status_code}]: {response.reason}"
        )
        return None
    except (
        requests.exceptions.Timeout,
        requests.exceptions.RequestException,
    ) as e:
        if isinstance(e, requests.exceptions.Timeout):
            message = (
                f"timeout [{config.timeout} second(s)] "
                f"fetching {type} data: {url}"
            )
        else:
            message = f"exception raised fetching {type} data: {url}: {e}"

        logger.error(message)
        return None
