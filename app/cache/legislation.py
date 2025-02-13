# isort: skip_file
# fmt: off
# flake8: noqa

import logging
import re
import xml.etree.ElementTree as ET  # nosec BXXX

from typing import Optional

import requests  # type: ignore

from app.cache.construction_legislation import construction_legislation_dataframe
from app.search.config import SearchDocumentConfig
from app.search.utils.date import convert_date_string_to_obj
from app.search.utils.documents import (  # noqa: E501
    generate_short_uuid,
    insert_or_update_document,
)
from app.search.utils.retrieve_data import get_data_from_url

logger = logging.getLogger(__name__)


def _get_text_from_element(element: Optional[ET.Element]) -> Optional[str]:
    """
    Extracts and returns the text content from an XML element if it exists.

    This function checks if the provided XML element is not None.
    If the element is available, it returns the text content of that element.
    If the element is None, it returns None.

    Parameters:
        element (Optional[ET.Element]):
            The XML element from which to extract the text.

    Returns:
        Optional[str]:
            The text content of the element if it exists, otherwise None.
    """
    try:
        return element.text if element is not None else None
    except Exception as e:
        logger.error(f"error extracting text from element: {e}")
        return None


def _update_result_dict(result_dict: dict, url, key: str, value):
    """
    Update the result dictionary with the given key and value.

    Parameters:
    - result_dict: Dictionary to update.
    - key: Key to update in the dictionary.
    - value: Value to assign to the key in the dictionary.

    Returns:
    - None
    """

    datum = {"key": key, "value": value}
    if url not in result_dict:
        result_dict[url] = []
    result_dict[url].append(datum)


class Legislation:
    def __init__(self):
        """
        Initializes the class instance and defines the XML namespaces.

        Attributes:
            _namespaces (dict):
                A dictionary containing XML namespaces with their
                corresponding URLs. These namespaces are used to
                refer to elements in XML documents adhering to
                different XML schemas.
        """
        # Define the XML namespaces
        self._namespaces = {
            "leg": "http://www.legislation.gov.uk/namespaces/legislation",
            "dc": "http://purl.org/dc/elements/1.1/",
            "dct": "http://purl.org/dc/terms/",
            "atom": "http://www.w3.org/2005/Atom",
            "ukm": "http://www.legislation.gov.uk/namespaces/metadata",
        }

    def build_cache(self, config: SearchDocumentConfig):
        """
        Builds a cache of legislation documents by retrieving XML data from
        URLs specified in a DataFrame.

        Parameters:
        config (SearchDocumentConfig): Configuration object for searching
        documents.

        Raises:
        Exception: If there's an error fetching data from the URL or no data
        is returned.

        Functionality:
        1. Logs the start of the caching process.
        2. Loads legislation data into a DataFrame.
        3. Iterates over each row in the DataFrame to fetch XML data from
            specified URLs.
        4. Extracts and parses XML data, logging relevant informational
            and error messages.
        5. Extracts specific fields (identifier, title, description, etc.)
            from the parsed XML data.
        6. Converts the extracted data to JSON format.
        7. Inserts or updates the document in the cache.
        8. Logs errors and re-raises them if data retrieval fails.
        """
        logger.info("building legislation cache...")
        dataset = construction_legislation_dataframe()

        results_dict = {}  # type: ignore

        # For each row, get the URL from the column named
        # 'URI to Extract XML Data'
        # and store the XML data in a list
        for index, row in dataset.iterrows():
            base_url = row["URI to Extract XML Data"]
            logger.info(
                f"fetching data from page {index + 1} / "
                f"{len(dataset)}: {base_url}..."
            )

            try:
                data = get_data_from_url(config, base_url, "legislation")

                if data is None:
                    _update_result_dict(results_dict, base_url, "FAILED", "no data returned")
                    if index == len(dataset) - 1:
                        logger.error("no more URLs to fetch. exiting the process...")
                        break
                    logger.warning("trying to fetch data from the next URL...")
                    continue

                if data:
                    logger.debug(f"parsing data from {base_url}...")
                    root = ET.fromstring(data)  # nosec BXXX

                    identifier = _get_text_from_element(
                        root.find(".//dc:identifier", self._namespaces)
                    )  # nosec BXXX
                    _update_result_dict(results_dict, base_url,
                                        ".//dc:identifier", "key not found"
                                        if identifier is None else identifier)


                    title = _get_text_from_element(
                        root.find(".//dc:title", self._namespaces)
                    )  # nosec BXXX
                    _update_result_dict(results_dict, base_url,
                                        ".//dc:title", "key not found"
                                        if title is None else title)

                    description = _get_text_from_element(
                        root.find(".//dc:description", self._namespaces)
                    )  # nosec BXXX
                    _update_result_dict(results_dict, base_url,
                                        ".//dc:description", "key not found"
                                        if description is None else description)

                    format = _get_text_from_element(
                        root.find(".//dc:format", self._namespaces)
                    )  # nosec BXXX
                    _update_result_dict(results_dict, base_url,
                                        ".//dc:format", "key not found"
                                        if format is None else format)

                    language = _get_text_from_element(
                        root.find(".//dc:language", self._namespaces)
                    )  # nosec BXXX
                    _update_result_dict(results_dict, base_url,
                                        ".//dc:language", "key not found"
                                        if language is None else language)

                    publisher = _get_text_from_element(
                        root.find(".//dc:publisher", self._namespaces)
                    )  # nosec BXXX
                    _update_result_dict(results_dict, base_url,
                                        ".//dc:publisher", "key not found"
                                        if publisher is None else publisher)

                    modified = _get_text_from_element(
                        root.find(".//dc:modified", self._namespaces)
                    )  # nosec BXXX
                    _update_result_dict(results_dict, base_url,
                                        ".//dc:modified", "key not found"
                                        if modified is None else modified)

                    valid = _get_text_from_element(
                        root.find(".//dct:valid", self._namespaces)
                    )  # nosec BXXX
                    _update_result_dict(results_dict, base_url,
                                        ".//dct:valid", "key not found"
                                        if valid is None else valid)

                    document_json = self._to_json(
                        description,
                        format,
                        identifier,
                        language,
                        modified,
                        publisher,
                        title,
                        valid,
                    )

                    # Insert or update the document
                    insert_or_update_document(document_json)
            except Exception as e:
                _update_result_dict(results_dict, base_url, "FAILED-EXCEPTION", e)

                logger.error(f"error fetching data from {base_url}: {e}")
                if index == len(dataset) - 1:
                    logger.error("no more URLs to fetch. exiting the process...")
                    break
                logger.warning("trying to fetch data from the next URL...")
                continue

        total_urls = len(results_dict)
        failed_urls = len([url for url in results_dict if results_dict[url] is not None])
        failed_exception_urls = len([url for url in results_dict
                                     if results_dict[url] is not None
                                     and "FAILED-EXCEPTION" in results_dict[url]])
        logger.info(f"total URLs: {total_urls}")
        logger.warning(f"failed URLs: {failed_urls}")
        logger.warning(f"failed URLs with exception: {failed_exception_urls}")

    def _to_json(
        self,
        description,
        format,
        identifier,
        language,
        modified,
        publisher,
        title,
        valid,
    ):
        """
        Converts given parameters into a JSON-like dictionary format.

        Arguments:
        description (str): Description of the item.
        format (str): Format of the item.
        identifier (str): Unique identifier for the item.
        language (str): Language in which the item is available.
        modified (str): The date when the item was last modified.
        publisher (str): The publisher of the item.
        title (str): The title of the item.
        valid (str): The date until which the item is considered valid.

        Returns:
        dict: A dictionary containing the item details in a structured format.
        """

        valid_sort_date = modified if valid is None or valid == "" else valid

        return {
            "id": generate_short_uuid(),
            "title": title,
            "identifier": identifier,
            "publisher": publisher,
            "publisher_id": (
                None
                if publisher is None
                else re.sub(
                    r"[^a-zA-Z0-9]", "", publisher.replace(" ", "").lower()
                )
            ),
            "language": language if language is not None else "eng",
            "format": format if format is not None else "",
            "description": description if description is not None else "",
            "date_issued": convert_date_string_to_obj(valid_sort_date),
            "date_modified": convert_date_string_to_obj(modified),
            "date_valid": valid_sort_date,
            "sort_date": valid_sort_date,
            "type": "Legislation",
        }
