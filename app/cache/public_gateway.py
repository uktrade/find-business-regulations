import json
import logging
import re
import time

import requests  # type: ignore

from bs4 import BeautifulSoup

from app.search.utils.date import convert_date_string_to_obj
from app.search.utils.documents import (  # noqa: E501
    generate_short_uuid,
    insert_or_update_document,
)

logger = logging.getLogger(__name__)


def _build_like_conditions(field, and_terms, or_terms):
    """

    Generates SQL LIKE conditions.

    Args:
        field (str): The database field to apply the LIKE condition to.
        terms (list of str): A list of terms to include in the LIKE
                             condition.

    Returns:
        str: A string containing the LIKE conditions combined with 'OR'.
    """
    # Put each term into the list
    terms = and_terms

    # If there are OR terms, then put an OR condition between them
    if or_terms:
        terms.append("(" + " OR ".join(or_terms) + ")")

    return " OR ".join([f"{field} LIKE LOWER('%{term}%')" for term in terms])


def _fetch_title_from_url(url):
    """
    Fetches the title from the given URL.

    Args:
        url (str): The URL to fetch the title from.

    Returns:
        str: The title extracted from the meta tag or the page title.
    """
    try:
        # Ensure the URL has a schema
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        response = requests.get(url, timeout=2)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Try to find the DC.title meta tag
        title_tag = soup.find("meta", {"name": "DC.title"})
        if title_tag and title_tag.get("content"):
            return title_tag["content"]

        # If DC.title is not found, search for pageTitle in the body
        page_title = soup.select_one("#layout1 #layout2 #pageTitle")
        if page_title:
            return page_title.get_text(strip=True)

        logger.warning(f"title not found in {url}")
    except Exception as e:
        logger.error(f"error fetching title from {url}: {e}")

    # No title found therefore return empty string
    return ""


class PublicGateway:
    def __init__(self):
        """
        Initializes the API client with the base URL for the Trade Data API.

        Attributes:
            base_url (str): The base URL of the Trade Data API.
        """
        self._base_url = (
            "https://data.api.trade.gov.uk/v1/datasets/fbr-regulations"
            "/versions/v1.0.1/data"
        )

    def build_cache(self, config):
        logger.info("fetching all data from orpd...")

        # URL encode the query for the API request
        params = {"format": "json"}

        # Start time
        start_time = time.time()

        # Make the GET request
        response = requests.get(
            self._base_url,
            params=params,
            timeout=config.timeout,  # nosec BXXX
        )

        # End time
        end_time = time.time()
        initial_request_system_time = end_time - start_time

        logger.debug(
            f"fetching all data from orpd took "
            f"{initial_request_system_time} seconds"
        )

        # Check if the request was successful
        if response.status_code == 200:
            data = json.loads(response.text)

            # Now you can use `data` as a usual Python dictionary
            # Convert each row into DataResponseModel object
            total_documents = len(data.get("uk_regulatory_documents"))
            inserted_document_count = 1
            for row in data.get("uk_regulatory_documents"):
                # Start time
                start_time = time.time()

                logger.info(
                    f"inserting or updating document "
                    f"{inserted_document_count} / ({total_documents})..."
                )

                # Normalize the date fields
                row["date_issued"] = convert_date_string_to_obj(
                    row.get("date_issued")
                )
                row["date_modified"] = convert_date_string_to_obj(
                    row.get("date_modified")
                )
                row["date_valid"] = convert_date_string_to_obj(
                    row.get("date_valid")
                )
                row["id"] = generate_short_uuid()

                row["publisher_id"] = (
                    None
                    if row["publisher"] is None
                    else re.sub(
                        r"[^a-zA-Z0-9]",
                        "",
                        row["publisher"].replace(" ", "").lower(),
                    )
                )

                # Process related_legislation field
                if row.get("related_legislation"):
                    related_legislation_urls = row[
                        "related_legislation"
                    ].split("\n")

                    related_legislation = []
                    for url in related_legislation_urls:
                        try:
                            title = _fetch_title_from_url(url)
                        except Exception as e:
                            logger.error(
                                f"error fetching title from {url}: {e}"
                            )
                            title = ""

                        related_legislation.append(
                            {
                                "url": url,
                                "title": title if title != "" else url,
                            }
                        )
                    row["related_legislation"] = related_legislation

                # End time
                end_time = time.time()
                process_related_legislation_time = end_time - start_time
                logger.info(
                    f"row {row["id"]} took "
                    f"{process_related_legislation_time} seconds to process"
                )
                insert_or_update_document(row)
                inserted_document_count += 1
            return response.status_code, inserted_document_count
        else:
            logger.error(
                f"error fetching data from orpd: {response.status_code}"
            )
