import csv
import http
import json
import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from app.core.forms import RegulationSearchForm
from app.search.config import SearchDocumentConfig
from app.search.utils.search import search, search_database

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def document(request: HttpRequest, id) -> HttpResponse:
    """
    Handles the request to retrieve and display a document based on an
    identifier (id). It validates the presence of the id parameter, sanitizes
    inputs, performs a database search, and prepares the context to render the
    results. If the requested document is not found or an error occurs,
    appropriate error details are included in the response.

    Args:
        request (HttpRequest): The HTTP request object containing metadata,
            user data, and cookies related to the HTTP request.
        id (str): The identifier for the document to be retrieved. It is
            mandatory for processing the request.

    Returns:
        HttpResponse: The HTTP response containing the rendered template with
            the provided context data. It includes the document details, status
            codes, or error information based on the request's outcome.

    Raises:
        Exception: Captures and logs any unexpected errors occurring during the
            execution of the function.
    """
    context = {
        "service_name": settings.SERVICE_NAME,
    }

    if not id:
        context["status_code"] = http.HTTPStatus.BAD_REQUEST
        return render(
            request, template_name="page_not_found.html", context=context
        )

    # Create a search configuration object with the provided id
    config = SearchDocumentConfig(search_query="", id=id)
    config.sanitize_all_if_needed()
    config.print_to_log("document endpoint")

    try:
        queryset = search_database(config)

        if not queryset:
            context["status_code"] = http.HTTPStatus.NOT_FOUND
            return render(
                request, template_name="page_not_found.html", context=context
            )

        context["result"] = queryset.first()
        context["result"].regulatory_topics = context[
            "result"
        ].regulatory_topics.split("\n")
        context["status_code"] = http.HTTPStatus.OK

        # Parse the related_legislation field
        related_legislation_str = context["result"].related_legislation

        if related_legislation_str is not None:
            try:
                related_legislation_json = json.loads(
                    related_legislation_str.replace("'", '"')
                )
                context["result"].related_legislation = (
                    related_legislation_json
                )
            except json.JSONDecodeError as e:
                logger.error(f"JSON decoding error: {e}")
                context["error"] = f"error fetching details: {e}"
                context["result"].related_legislation = []
    except Exception as e:
        logger.error("error fetching details: %s", e)
        context["error"] = f"error fetching details: {e}"

    return render(request, template_name="document.html", context=context)


@require_http_methods(["GET"])
def search_django(request: HttpRequest):
    """
    Search view.

    Renders the Django based search page.
    """
    form = RegulationSearchForm(request.GET)
    search_term = request.GET.get("search", "")

    context = {
        "service_name": settings.SERVICE_NAME,
        "service_name_long": settings.SERVICE_NAME_LONG,
        "form": form,
        "search_term": search_term,
    }
    context = search(context, request)

    return render(request, template_name="django-fbr.html", context=context)


@require_http_methods(["GET"])
def search_react(request: HttpRequest) -> HttpResponse:
    """
    Search view.

    Renders the React based search page.
    """
    context = {
        "service_name": settings.SERVICE_NAME,
        "service_name_long": settings.SERVICE_NAME_LONG,
    }
    return render(request, template_name="react-fbr.html", context=context)


def _get_base_url(request: HttpRequest) -> str:
    """
    Get the base URL from the current request dynamically.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        str: The base URL (e.g., http://localhost:8081 or
             https://staging.example.com)
    """
    base_url = f"{request.scheme}://{request.get_host()}"
    return base_url


def download_csv(request):
    """
    Download CSV view.

    Handles the GET request to download the search results in CSV format.
    """
    logger.debug("building CSV downloadable file")
    context = {
        "service_name": settings.SERVICE_NAME,
    }

    try:
        logger.debug("searching for all documents")
        response_data = search(context, request, ignore_pagination=True)
        logger.debug(f"response_data length: {len(response_data)}")
        base_url = _get_base_url(request)

        search_results = []
        for result in response_data:
            search_results.append(
                {
                    "title": result.title,
                    "publisher": result.publisher,
                    "description": result.description,
                    "type": result.type,
                    "date_valid": result.date_valid,
                    "document_url": f"{base_url}/document/{result.id}",
                }
            )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="search_results.csv"'
        )

        writer = csv.DictWriter(response, fieldnames=search_results[0].keys())
        writer.writeheader()
        writer.writerows(search_results)
        return response
    except Exception as e:
        logger.error("error downloading CSV: %s", e)
        return HttpResponse(
            content="error downloading CSVs",
            status=500,
        )
