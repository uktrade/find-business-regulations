import logging
import time

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import QuerySet

from app.search.config import SearchDocumentConfig

logger = logging.getLogger(__name__)


def paginate(
    context: dict, config: SearchDocumentConfig, results: QuerySet
) -> dict:
    """
    Paginates the given query set and updates the context with
    pagination details.

    Parameters:
    - context (dict):
        The context dictionary to be updated with pagination details.
    - config (SearchDocumentConfig):
        Configuration object containing limit and offset for pagination.
    - results (QuerySet): The query set of documents to be paginated.

    Returns:
    - dict:
        The updated context dictionary containing pagination information and
        paginated documents.

    Logs the time taken for the pagination process in different stages:
    1. Time taken to paginate the documents.
    2. Time taken to process regulatory topics for each document.
    3. Time taken to update the context with pagination details.

    Handles pagination exceptions:
    - If the page is not an integer, defaults to the first page.
    - If the page is empty, defaults to the last page.

    Converts the paginated documents into a list of JSON objects with keys:
    - "id"
    - "title"
    - "publisher"
    - "description"
    - "type"
    - "date_modified"
    - "date_valid"
    - "regulatory_topics"

    Updates the context with:
    - Paginator object.
    - Paginated documents in JSON format.
    - Total number of results in the current page.
    - Boolean to indicate if pagination is needed.
    - Total number of results.
    - Total number of pages.
    - Current page number.
    - Start index of the results in the current page.
    - End index of the results in the current page.
    """
    start_time = time.time()

    logger.debug("paginating documents...")
    paginator = Paginator(results, config.limit)
    try:
        paginated_documents = paginator.page(config.offset)
    except PageNotAnInteger:
        paginated_documents = paginator.page(1)
    except EmptyPage:
        paginated_documents = paginator.page(paginator.num_pages)

    end_time = time.time()
    logger.debug(
        f"time taken to paginate (before description +/ regulatory topics):"
        f" {round(end_time - start_time, 2)} seconds"
    )

    # Iterate over each document in paginated_documents
    if paginated_documents:
        start_time = time.time()

        for paginated_document in paginated_documents:
            if hasattr(paginated_document, "regulatory_topics"):
                regulatory_topics = paginated_document.regulatory_topics
                if regulatory_topics:
                    paginated_document.regulatory_topics = str(
                        regulatory_topics
                    ).split("\n")

        end_time = time.time()
        logger.debug(
            f"time taken to paginate "
            f"(after description +/ regulatory topics): "
            f"{round(end_time - start_time, 2)} seconds"
        )

    # Convert paginated_documents into a list of json objects
    paginated_documents_json = []
    for paginated_document in paginated_documents:
        paginated_documents_json.append(
            {
                "id": paginated_document.id,
                "title": paginated_document.title,
                "publisher": paginated_document.publisher,
                "description": paginated_document.description,
                "type": paginated_document.type,
                "date_modified": paginated_document.date_modified,
                "date_valid": paginated_document.date_valid,
                "regulatory_topics": paginated_document.regulatory_topics,
            }
        )

    start_time = time.time()
    context["paginator"] = paginator
    context["paginated_document_results"] = paginated_documents
    context["results"] = paginated_documents_json
    context["results_count"] = len(paginated_documents)
    context["is_paginated"] = paginator.num_pages > 1
    context["results_total_count"] = paginator.count
    context["results_page_total"] = paginator.num_pages
    context["current_page"] = config.offset
    context["start_index"] = paginated_documents.start_index()
    context["end_index"] = paginated_documents.end_index()
    end_time = time.time()

    logger.debug(
        f"time taken to paginate (after adding to context): "
        f"{round(end_time - start_time, 2)} seconds"
    )
    return context
