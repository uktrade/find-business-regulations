import base64
import json
import uuid

import requests  # type: ignore

from bs4 import BeautifulSoup
from numpy.f2py.auxfuncs import throw_error

from app.search.models import DataResponseModel, logger


def clear_all_documents():
    """
    Clears all documents from the 'DataResponseModel' table in the database.

    Logs the process of clearing the documents and handles any exceptions
    that may occur. If an error occurs, it logs the error message and
    raises an error.

    Raises:
        CustomError: If there is an error while clearing the documents.
    """
    logger.debug("clearing all documents from table...")
    try:
        DataResponseModel.objects.all().delete()
        logger.debug("documents cleared from table")
    except Exception as e:
        logger.error(f"error clearing documents: {e}")


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

        logger.debug(f"fetching title from {url}")
        response = requests.get(url, timeout=config.timeout)
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


def update_related_legislation_titles(config):
    try:
        documents = DataResponseModel.objects.all()

        for document in documents:
            related = document.related_legislation
            json_compatible_string = related.replace("'", '"')
            related_legislation_list = json.loads(json_compatible_string)

            logger.debug(
                f"related_legislation_list: {related_legislation_list}"
            )

            for related in related_legislation_list:
                found_title = _fetch_title_from_url(config, related["url"])
                logger.debug(f"found title: {found_title}")
                related["title"] = found_title

            document.related_legislation = json.dumps(related_legislation_list)
            document.save()
    except Exception as e:
        logger.error(f"error updating related legislation titles: {e}")
        throw_error(f"error updating related legislation titles: {e}")


def insert_or_update_document(document_json):
    """
    Inserts or updates a database document based on the given JSON data.

    The function first attempts to create a new document using the
    provided JSON data.

    If the document already exists (detected through an exception),
    it catches the error and tries to update the existing document instead.

    Args:
        document_json (dict): A dictionary containing the data for the
        document to be inserted or updated.

    Raises:
        Exception: If an error occurs during either the insert or update
        operation, the error is logged and re-raised.

    Logs:
        Logs detailed debug messages for each step, including the document
        being inserted, any errors encountered, and the outcome of the update
        operation.
    """
    try:
        logger.debug("creating document...")
        logger.debug(f"document: {document_json}")
        document = DataResponseModel(**document_json)
        document.full_clean()
        document.save()
    except Exception as e:
        logger.error(f"error creating document: {document_json}")
        logger.error(f"error: {e}")
        logger.debug("document already exists, updating...")

        # If a duplicate key error occurs, update the existing document
        try:
            document = DataResponseModel.objects.get(pk=document_json["id"])
            for key, value in document_json.items():
                setattr(document, key, value)
            document.save()
            logger.debug(f"document updated: {document}")
        except Exception as e:
            logger.error(f"error updating document: {document_json}")
            logger.error(f"error: {e}")
            throw_error(f"error updating document: {document_json}")


def generate_short_uuid():
    """
    Generates a short, URL-safe UUID.

    Returns:
        str: A URL-safe base64 encoded UUID truncated to 22 characters.
    """
    uid = uuid.uuid4()

    # Encode it to base64
    uid_b64 = base64.urlsafe_b64encode(uid.bytes).rstrip(b"=").decode("ascii")
    return uid_b64[
        :22
    ]  # Shorten as needed, typically more than 22 characters are
    # unnecessary and remain unique.
