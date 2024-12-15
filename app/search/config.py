import logging

from app.search.utils.terms import sanitize_input

logger = logging.getLogger(__name__)


class SearchDocumentConfig:
    def __init__(
        self,
        search_query: str,
        document_types=None,
        timeout=None,
        limit=10,
        offset=1,
        publisher_names=None,
        sort_by=None,
        id=None,
    ):
        """
        Initializes the SearchRequest object with the given parameters.

        Args:
            search_query (str): The search query string.
            document_types (Optional[List[str]]):
                A list of document types to filter by. Defaults to None.
            timeout (Optional[int]):
                The timeout value for the request in seconds. Defaults to None.
            limit (int):
                The maximum number of search results to return. Defaults to 10.
            offset (int):
                The starting position of the search results. Defaults to 1.
            publisher_names (Optional[List[str]]):
                A list of publisher names to filter by. Defaults to None.
            sort_by (Optional[str]):
                The field by which to sort the search results. Defaults to
                None.
            id (Optional[str]):
                An optional identifier for the search request. Defaults to
                None.

        Attributes:
            search_query (str): The search query string.
            document_types (Optional[List[str]]):
                A list of document types to filter by.
            timeout (Optional[int]):
                The timeout value for the request in seconds.
            limit (int): The maximum number of search results to return.
            offset (int): The starting position of the search results.
            publisher_names (Optional[List[str]]):
                A list of publisher names to filter by.
            sort_by (Optional[str]):
                The field by which to sort the search results.
            id (Optional[str]):
                An optional identifier for the search request.
        """
        self.search_query = search_query
        self.document_types = (
            None
            if document_types is None
            else [doc_type.lower() for doc_type in document_types]
        )
        self.timeout = None if timeout is None else int(timeout)
        self.limit = limit
        self.offset = offset
        self.publisher_names = (
            None
            if publisher_names is None
            else [pub_name.lower() for pub_name in publisher_names]
        )
        self.sort_by = sort_by
        self.id = id

        logger.info(f"document_types from request: {self.document_types}")
        logger.info(f"publisher_names from request: {self.publisher_names}")

    def sanitize_all(self):
        # Sanitize document types
        self.search_query = sanitize_input(self.search_query)

        # Sanitize document types
        if self.document_types:
            self.document_types = [
                sanitize_input(doc_type) for doc_type in self.document_types
            ]

        # Sanitize publisher names
        if self.publisher_names:
            self.publisher_names = [
                sanitize_input(pub_name) for pub_name in self.publisher_names
            ]

        # Sanitize sort_by
        if self.sort_by:
            self.sort_by = sanitize_input(self.sort_by)

        # Sanitize id
        if self.id:
            self.id = sanitize_input(self.id)

    def validate(self):
        """
        Validates the constraints defined for offset, limit,
        and sort_by attributes.

        Returns:
        bool
            True if all constraints are satisfied, False otherwise.

        Notes:
        - The offset must be a non-negative integer.
        - The limit must be a non-negative integer.
        - The sort_by attribute, if specified, must be either
            'recent' or 'relevance'.

        Errors are logged if any of the constraints are violated.
        """
        if self.offset < 0:
            logger.error("offset must be a positive integer")
            return False

        if self.limit < 0:
            logger.error("limit must be a positive integer")
            return False

        if self.sort_by:
            if self.sort_by not in ["recent", "relevance"]:
                logger.error("sort_by must be 'recent' or 'relevance'")
                return False
        return True

    def print_to_log(self):
        """

        Logs the current state of various search parameters.

        Logs the following attributes:
        - search_query: The search query string.
        - document_types: The list of document types being searched.
        - timeout: The timeout value for the search query.
        - limit: The maximum number of results to return.
        - offset: The starting point from which results are returned.
        - publisher_names: The list of publisher names to filter the search.
        - sort_by: The criteria for sorting the search results.
        - id: The unique identifier for the search query.

        """
        logger.info(f"search_query: {self.search_query}")
        logger.info(f"document_types: {self.document_types}")
        logger.info(f"timeout: {self.timeout}")
        logger.info(f"limit: {self.limit}")
        logger.info(f"offset: {self.offset}")
        logger.info(f"publisher_names: {self.publisher_names}")
        logger.info(f"sort_by: {self.sort_by}")
        logger.info(f"id: {self.id}")
