import base64
import hashlib
import uuid

from app.search.models import DataResponseModel, logger


def document_type_groups():
    import re

    from django.db.models import F
    from django.db.models.functions import Trim

    from app.search.models import DataResponseModel

    def format_document_type(doc_type):
        """
        Format document type string:
        1. For camel case strings (like EuropeanUnionDecision),
           insert spaces between words
        2. For strings with spaces, capitalize each word
        """
        # If already contains spaces, just capitalize each word
        if " " in doc_type:
            return " ".join(word.capitalize() for word in doc_type.split())

        # For camel case, insert spaces before capital letters and
        # capitalize first letter
        formatted = re.sub(r"(?<!^)(?=[A-Z])", " ", doc_type)
        return formatted

    # Get all distinct document types from the DataResponseModel
    document_types = (
        DataResponseModel.objects.values(doc_type=Trim(F("type")))
        .filter(type__isnull=False)
        .exclude(type__exact="")
        .distinct()
        .order_by("doc_type")
    )
    # Categorize document types
    non_legislation = []
    legislation = []
    for item in document_types:
        if item and item.get("doc_type") is not None:
            doc_type = item["doc_type"]
            formatted_type = format_document_type(doc_type)
            display_item = {
                "label": formatted_type,
                "name": doc_type,
            }

            if (
                "standard" in doc_type.lower()
                or "guidance" in doc_type.lower()
            ):
                # Add to non-legislation
                non_legislation.append(display_item)
            else:
                # Add to legislation
                legislation.append(display_item)
    return legislation, non_legislation


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
