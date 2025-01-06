# flake8: noqa
# isort: skip_file

import logging
import re
import time

from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)  # noqa
from django.db.models import F, Func, Q, QuerySet
from django.http import HttpRequest

from app.search.config import SearchDocumentConfig
from app.search.models import DataResponseModel
from app.search.utils.documents import calculate_score
from app.search.utils.paginate import paginate

logger = logging.getLogger(__name__)


def create_search_query(search_string):
    """
    Create a search query from a search string with
    implicit AND for space-separated words
    and explicit AND/OR operators.

    :param search_string: The search string to parse
    :return: A combined SearchQuery object
    """
    # Split the string into tokens, handling quoted phrases and operators
    tokens = re.findall(r'"[^"]+"|\bAND\b|\bOR\b|\w+', search_string)

    # Validate tokens to avoid issues with syntax
    if not tokens:
        return None  # Return None for empty or invalid input

    # Initialize variables
    query = None
    current_operator = "&"  # Default to implicit AND for space-separated words

    # Process tokens
    for token in tokens:
        if token.upper() == "AND":
            current_operator = "&"
        elif token.upper() == "OR":
            current_operator = "|"
        else:
            # Handle phrases and plain text
            is_phrase = token.startswith('"') and token.endswith('"')
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

            # Reset the operator to implicit AND for the next token
            current_operator = "&"

    return query


def search_database(config: SearchDocumentConfig):
    """
    Search the database for documents based on the search query.

    :param config: The search configuration object
    :return: A QuerySet of DataResponseModel objects
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
    query_objs = create_search_query(query_str)
    logger.debug(f"search query objects: {query_objs}")

    # Search across specific fields
    vector = SearchVector("title", "description", "regulatory_topics")
    queryset = DataResponseModel.objects.all()

    if query_objs:
        # Use the parsed query objects for strict filtering
        queryset = queryset.annotate(search=vector).filter(
            Q(search=query_objs)
        )
    else:
        queryset = queryset.annotate(search=vector)

    # Add partial matches for fallback, if desired
    # if config.search_query:
    # query_chunks = query_str.split()
    # partial_matches = Q()
    # for chunk in query_chunks:
    #     partial_matches |= (
    #         Q(title__icontains=chunk)
    #         | Q(description__icontains=chunk)
    #         | Q(regulatory_topics__icontains=chunk)
    #     )
    # queryset = queryset.filter(partial_matches)

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
        return queryset.order_by("-sort_date")

    if config.sort_by == "relevance":
        calculate_score(config, queryset)
        return queryset.order_by("-score")

    return queryset


def search(
    context: dict, request: HttpRequest, ignore_pagination=False
) -> dict | QuerySet[DataResponseModel]:
    logger.info("received search request: %s", request)
    start_time = time.time()

    search_query = request.GET.get("query", request.GET.get("search", ""))
    document_types = request.GET.getlist("document_type", [])
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
    config.print_to_log()

    # Search across specific fields
    results = search_database(config)

    logger.info("search results from database: %s", results)

    if ignore_pagination:
        logger.info("ignoring pagination")
        return results

    # convert search_results into json
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

    logger.info("search results from context: %s", context)
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
