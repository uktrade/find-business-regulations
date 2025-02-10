import base64
import uuid

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
