import json
import logging
import re
import time

from bs4 import BeautifulSoup

from app.search.utils.date import convert_date_string_to_obj
from app.search.utils.documents import insert_or_update_document  # noqa: E501
from app.search.utils.retrieve_data import get_data_from_url

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


def _fetch_title_from_url(config, url):
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

        data = get_data_from_url(config, url, "oprd/gw")

        if data:
            logger.debug(f"data from {url}: {data}")

        soup = BeautifulSoup(data, "html.parser")

        # Try to find the DC.title meta tag
        title_tag = soup.find("meta", {"name": "DC.title"})
        if title_tag:
            logger.debug(f"title found in {url}: {title_tag}")

        content = title_tag.get("content")
        if content:
            logger.debug(f"content found in {url}: {content}")

        if title_tag and content:
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


def rectify_malformed_json_to_list(input_string):
    """
    Convert a malformed JSON-like string to valid JSON.

    Args:
        input_string (str): The malformed JSON-like string to convert
        output_file (str, optional): Path to save the JSON file.
        If None, file is not saved.

    Returns:
        str: The valid JSON string
    """
    # Clean the string and prepare for parsing
    input_string = input_string.strip()
    items = re.findall(r"\{([^}]+)\}", input_string)

    # Parse each item into a proper dictionary
    result = []
    for item in items:
        # Split by comma, but only outside of quotes
        parts = [p.strip() for p in item.split(",")]
        obj = {}

        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip()
                value = value.strip()
                obj[key] = value

        result.append(obj)
    return result


class PublicGateway:
    def __init__(self):
        """
        Initializes the API client with the base URL for the Trade Data API.

        Attributes:
            base_url (str): The base URL of the Trade Data API.
        """
        self._base_url = (
            "https://data.api.trade.gov.uk/v1/datasets/uk-business-regulations"
            "/versions/latest/data"
        )

    def build_cache(self, config):
        logger.info("fetching all data from public gateway...")

        # URL encode the query for the API request
        params = {"format": "json"}

        # Start time
        start_time = time.time()

        data = get_data_from_url(
            config, self._base_url, "exception raised fetching", params
        )
        inserted_document_count = 1

        # End time
        end_time = time.time()
        initial_request_system_time = end_time - start_time

        logger.debug(
            f"fetching all data from public gateway took "
            f"{initial_request_system_time} seconds"
        )

        # Check if the request was successful
        if data:
            data = json.loads(data)

            # Now you can use `data` as a usual Python dictionary
            # Convert each row into DataResponseModel object
            total_documents = len(data.get("uk_legislation_pdg"))

            for row in data.get("uk_legislation_pdg"):
                # Start time
                start_time = time.time()

                logger.info(
                    f"inserting or updating document "
                    f"{inserted_document_count} / ({total_documents})..."
                )

                # Unnormalized date fields
                row["source_date_issued"] = row.get("date_issued")

                row["source_date_modified"] = row.get("date_modified")

                row["source_date_valid"] = row.get("date_valid")

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

                row["sort_date"] = row["date_valid"]

                row["id"] = row.get("uuid", "")

                # Remove uuid from row
                row.pop("uuid", None)

                row["publisher_id"] = (
                    None
                    if row["publisher"] is None
                    else re.sub(
                        r"[^a-zA-Z0-9]",
                        "",
                        row["publisher"].replace(" ", "").lower(),
                    )
                )

                corrected_related_legislation = rectify_malformed_json_to_list(
                    row.get("related_legislation_dict")
                )
                corrected_related_legislation_json = json.dumps(
                    corrected_related_legislation
                )
                row["related_legislation"] = corrected_related_legislation_json

                # Remove related_legislation_dict from row
                row.pop("related_legislation_dict", None)

                end_time = time.time()
                process_related_legislation_time = end_time - start_time
                logger.debug(
                    f"row {row["id"]} took "
                    f"{process_related_legislation_time} seconds to process"
                )
                was_inserted = insert_or_update_document(row)
                if was_inserted:
                    inserted_document_count += 1
                else:
                    logger.error(
                        f"error inserting or updating document: {row}"
                    )
        else:
            logger.error("error fetching data from orpd: no data received")
            return 500, 0

        # return process_code, inserted_document_count
        return 200, inserted_document_count
