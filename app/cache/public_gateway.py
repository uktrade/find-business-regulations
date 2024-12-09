import json
import logging
import re

import requests  # type: ignore

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


class PublicGateway:
    def __init__(self):
        """
        Initializes the API client with the base URL for the Trade Data API.

        Attributes:
            base_url (str): The base URL of the Trade Data API.
        """
        self._base_url = (
            "https://data.api.trade.gov.uk/v1/datasets/orp-regulations"
            "/versions/v1.0.1/data"
        )

    def build_cache(self, config):
        logger.info("fetching all data from orpd...")

        # URL encode the query for the API request
        params = {"format": "json"}

        # Make the GET request
        response = requests.get(
            self._base_url,
            params=params,
            timeout=config.timeout,  # nosec BXXX
        )

        # Check if the request was successful
        if response.status_code == 200:
            data = json.loads(response.text)

            # Now you can use `data` as a usual Python dictionary
            # Convert each row into DataResponseModel object
            total_documents = len(data.get("uk_regulatory_documents"))
            inserted_document_count = 1
            for row in data.get("uk_regulatory_documents"):
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

                insert_or_update_document(row)
                inserted_document_count += 1
            return response.status_code, inserted_document_count
        else:
            logger.error(
                f"error fetching data from orpd: {response.status_code}"
            )

            raise Exception(
                f"error fetching data from orpd: {response.status_code}"
            )
