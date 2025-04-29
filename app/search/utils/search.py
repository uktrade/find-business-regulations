# flake8: noqa
# isort: skip_file

import logging
import re
import time
from typing import Tuple, Union

from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
)  # noqa
from django.db.models import F, Func, Q, QuerySet
from django.http import HttpRequest

from app.search.config import SearchDocumentConfig
from app.search.models import DataResponseModel
from app.search.utils.calculate_score import calculate_score
from app.search.utils.documents import document_type_groups
from app.search.utils.paginate import paginate

logger = logging.getLogger(__name__)


def clean_up_tokens(search_string, all_phrases):
    """
    Parse search string into tokens, optionally wrapping all non-operator multi-word phrases in quotes.

    Args:
        search_string: The search query string to parse
        all_phrases: If True, all space-separated text (except operators) will be treated as phrases
                     and wrapped in quotes if not already quoted

    Returns:
        A cleaned search string with phrases properly quoted when all_phrases=True
    """
    if not search_string:
        return ""

    # First extract quoted phrases, operators, and individual words
    tokens = re.findall(r'"[^"]+"|\bAND\b|\bOR\b|\w+', search_string)

    if all_phrases:
        # Group non-operator, non-quoted consecutive words into phrases
        operators = {"AND", "OR"}
        quoted_tokens = []
        current_phrase = []

        for token in tokens:
            # Skip empty tokens
            if not token:
                continue

            # Check if token is already quoted
            is_quoted = token.startswith('"') and token.endswith('"')
            # Check if token is an operator
            is_operator = token in operators

            if is_quoted or is_operator:
                # If we have a phrase being built, finalize it first
                if current_phrase:
                    quoted_tokens.append(f'"{" ".join(current_phrase)}"')
                    current_phrase = []

                # Add the quoted phrase or operator as is
                quoted_tokens.append(token)
            else:
                # Add word to current phrase
                current_phrase.append(token)

        # Don't forget any remaining phrase
        if current_phrase:
            quoted_tokens.append(f'"{" ".join(current_phrase)}"')

        # Join the tokens back together with spaces
        return quoted_tokens

    return tokens


def create_search_query(
    search_string: str,
    ext_search_results: bool = False,
    xor_as_phrases: bool = False,
) -> Union[SearchQuery, Tuple[SearchQuery, int, int, int]]:
    """
    Create a search query from a search string with
    implicit AND for space-separated words
    and explicit AND/OR operators.

    :param search_string: The search string to parse
    :param ext_search_results: A flag to return additional search results
    :return: A combined SearchQuery object or a tuple with the query and counts
    """
    # Split the string into tokens, handling quoted phrases and operators

    tokens = clean_up_tokens(search_string, False)

    if xor_as_phrases:
        tokens = tokens + clean_up_tokens(search_string, xor_as_phrases)

    # Validate tokens to avoid issues with syntax
    if not tokens:
        return (
            None if not ext_search_results else (None, 0, 0, 0)
        )  # Return None for empty or invalid input

    # Initialize variables
    query = None
    current_operator = "|"  # Default to implicit OR for space-separated words

    # Process tokens
    num_ands = 0
    num_ors = 0
    num_phrases = 0
    for token in tokens:
        if token.upper() == "AND":
            current_operator = "&"
            num_ands += 1
        elif token.upper() == "OR":
            current_operator = "|"
            num_ors += 1
        else:
            # Handle phrases and plain text
            is_phrase = token.startswith('"') and token.endswith('"')

            if is_phrase:
                num_phrases += 1

            clean_token = token.strip('"')
            new_query = SearchQuery(
                clean_token, search_type="phrase" if is_phrase else "plain"
            )

            # Combine queries based on the current operator
            if query is None:
                query = new_query  # First token initializes the query
            else:
                if current_operator == "&":
                    query = query & new_query
                elif current_operator == "|":
                    query = query | new_query

            # Reset the operator to implicit OR for the next token
            current_operator = "|"

    if ext_search_results:
        return query, num_ands, num_ors, num_phrases

    return query


def search_database(config: SearchDocumentConfig):
    """
    Search for documents based on various criteria including ID, query string,
    document type, publisher, and sort preferences. Implements both strict
    and partial search capabilities.

    Args:
        config (SearchDocumentConfig): An object containing search configuration
            data such as query string, ID, document types, publishers, and sorting
            preferences.

    Returns:
        QuerySet: A Django QuerySet containing the filtered and optionally sorted
        search results.
    """
    # If an ID is provided, return the document with that ID
    if config.id:
        logger.debug(f"searching for document with id: {config.id}")
        try:
            return DataResponseModel.objects.filter(id=config.id)
        except DataResponseModel.DoesNotExist:
            return DataResponseModel.objects.none()

    # Sanitize the query string
    config.sanitize_all_if_needed()
    query_str = config.search_query
    logger.debug(f"sanitized search query: {query_str}")

    # Generate query object
    try:
        query_objs, num_ands, num_ors, num_phrases = create_search_query(
            query_str, True, True
        )
        logger.debug(f"search query objects: {query_objs}")
    except Exception as e:
        logger.error(f"error creating search query: {e}")
        query_objs = None
        num_ands = 0
        num_ors = 0
        num_phrases = 0

    # Search across specific fields
    vector = SearchVector("title", "description", "regulatory_topics")

    # Get all documents from the queryset
    queryset = DataResponseModel.objects.all()
    queryset = queryset.annotate(search=vector)

    # Use the parsed query objects for strict filtering
    if query_objs:
        queryset = queryset.annotate(search=vector).filter(
            Q(search=query_objs)
        )
    else:
        queryset = queryset.annotate(search=vector)

    # Add partial matches for fallback, if desired
    if (
        query_str
        and queryset.count()
        and num_ands == 0
        and num_ors == 0
        and num_phrases == 0
    ):
        logger.debug(
            "adding partial matches to search query as "
            "query string brought no results for strict search"
        )
        queryset = DataResponseModel.objects.all()
        query_chunks = query_str.split()
        partial_matches = Q()
        for chunk in query_chunks:
            partial_matches |= (
                Q(title__icontains=chunk)
                | Q(description__icontains=chunk)
                | Q(regulatory_topics__icontains=chunk)
            )
        queryset = queryset.filter(partial_matches)
        logger.debug("queryset values after partial matches: %s", queryset)

    # Filter by document types
    if config.document_types:
        query = Q()
        for doc_type in config.document_types:
            query |= Q(type__icontains=doc_type)
        queryset = queryset.filter(query)

    # Filter by publisher
    if config.publisher_names:
        query = Q()
        for publisher in config.publisher_names:
            query |= Q(publisher_id__icontains=publisher)
        queryset = queryset.filter(query)

    # Sort results based on the sort_by parameter
    if config.sort_by is None or config.sort_by == "recent":
        return queryset.order_by(F("sort_date").desc(nulls_last=True))

    if config.sort_by == "relevance":
        try:
            # Calculate the score for each document based on the search query
            queryset = calculate_score(query_objs, queryset)
        except Exception as e:
            logger.error(f"error calculating score for search: {e}")

    return queryset


def search(
    context: dict, request: HttpRequest, ignore_pagination=False
) -> dict | QuerySet[DataResponseModel]:
    logger.debug("received search request: %s", request)
    logger.debug("received search context: %s", context)
    logger.debug("ignore_pagination: %s", ignore_pagination)
    start_time = time.time()

    search_query = request.GET.get("query", request.GET.get("search", ""))
    document_types = request.GET.getlist("document_type", [])

    if "legislation" in document_types:
        legislation, _ = document_type_groups()
        # Create a set from document_types for O(1) lookups
        existing_types = set(document_types)

        # Filter and extend in one operation instead of checking and appending one by one
        new_types = [
            item.get("name")
            for item in legislation
            if item.get("name") is not None
            and item.get("name") not in existing_types
        ]

        # Add all new types at once
        document_types.extend(new_types)

    offset = request.GET.get("page", "1")
    offset = int(offset) if offset.isdigit() else 1
    limit = request.GET.get("limit", "10")
    limit = int(limit) if limit.isdigit() else 10
    publishers = request.GET.getlist("publisher", [])
    sort_by = request.GET.get("sort", None)

    # Get the search results from the Data API using PublicGateway class
    config = SearchDocumentConfig(
        search_query,
        document_types,
        limit=limit,
        offset=offset,
        publisher_names=publishers,
        sort_by=sort_by,
    )

    config.sanitize_all_if_needed()

    # Display the search query in the log
    config.print_to_log("search")

    # Search across specific fields
    results = search_database(config)
    logger.debug("search results from database: %s", results)

    if ignore_pagination:
        logger.info("ignoring pagination and returning results")
        return results

    # convert search_results into json
    logger.debug("building context for search results-pagination...")
    pag_start_time = time.time()
    context = paginate(context, config, results)
    pag_end_time = time.time()

    logger.debug(
        f"time taken to paginate (called from views.py): "
        f"{round(pag_end_time - pag_start_time, 2)} seconds"
    )

    end_time = time.time()
    logger.debug(
        f"time taken to search and produce response: "
        f"{round(end_time - start_time, 2)} seconds"
    )

    logger.debug("search results from context: %s", context)
    return context


class Trim(Func):
    function = "TRIM"
    template = "%(function)s(%(expressions)s)"


def get_publisher_names():
    logger.debug("getting publisher names...")
    publishers_list = []

    try:
        publishers_list = (
            DataResponseModel.objects.annotate(
                trimmed_publisher=Trim(F("publisher")),
                trimmed_publisher_id=Trim(F("publisher_id")),
            )
            .values(
                "trimmed_publisher",
                "trimmed_publisher_id",
            )
            .distinct()
        )
    except Exception as e:
        logger.error(f"error getting publisher names: {e}")
        logger.debug("returning empty list of publishers")

    logger.debug(f"publishers found: {publishers_list}")
    return publishers_list
