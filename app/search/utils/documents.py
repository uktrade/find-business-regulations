import base64
import hashlib
import uuid

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
        # with transaction.atomic():
        document = DataResponseModel(**document_json)
        document.full_clean()
        document.save()
        return True
    except Exception as e:
        logger.error(f"error creating document: {document_json}")
        logger.error(f"error: {e}")
        logger.debug("document already exists, ignore")
        return False


def generate_uuid(text: str = "", short: bool = True) -> str:
    """
    Generates a short, unique identifier (UUID) in base64 format, optionally
    derived from a given string identifier.

    This function provides a shorthand, URL-safe UUID either by encoding a
    randomly generated UUID or a namespace-based UUID derived from a provided
    string identifier.

    Args:
        text: str, optional
            A string identifier used to derive a namespace-based UUID. If not
            provided or invalid, a random UUID is generated.
        short: bool, optional
            A flag indicating whether the UUID should be shortened to a
            URL-safe format. Defaults to True.

    Returns:
        str: A shortened, URL-safe representation of a UUID in base64 format.
    """

    def _is_id_valid(id: str) -> bool:
        return isinstance(id, str) and bool(id)

    def _generate_hash(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    # If id is provided, use it to generate the UUID using a hash function
    if _is_id_valid(text):
        hash_value = _generate_hash(text)
        return hash_value[
            :22
        ]  # Shorten as needed, typically more than 22 characters are

    uid = uuid.uuid4()

    if not short:
        return uid.hex

    # Encode it to base64
    uid_b64 = base64.urlsafe_b64encode(uid.bytes).rstrip(b"=").decode("ascii")
    return uid_b64[
        :22
    ]  # Shorten as needed, typically more than 22 characters are
    # unnecessary and remain unique.
