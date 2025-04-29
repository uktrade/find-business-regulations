import logging
import time

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import QuerySet

from app.search.config import SearchDocumentConfig
from app.search.utils.date import format_partial_date_govuk
from app.search.utils.documents import document_type_groups

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
    - "source_date_modified"
    - "source_date_issued"
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

    legislation_types, non_legislation_types = document_type_groups()
    for paginated_document in paginated_documents:
        ptype = paginated_document.type
        label_type = ""

        # First check in legislation_types
        for item in legislation_types:
            if item.get("name") == ptype:
                label_type = item.get("label")
                break

        # If not found in legislation_types, check in non_legislation_types
        if not label_type:
            for item in non_legislation_types:
                if item.get("name") == ptype:
                    label_type = item.get("label")
                    break

        # If still not found, use the original type
        if not label_type:
            label_type = ptype

        paginated_documents_json.append(
            {
                "id": paginated_document.id,
                "title": paginated_document.title,
                "publisher": paginated_document.publisher,
                "description": paginated_document.description,
                "type": label_type,
                "source_date_modified": format_partial_date_govuk(
                    paginated_document.source_date_modified
                ),
                "source_date_issued": format_partial_date_govuk(
                    paginated_document.source_date_issued
                ),
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
