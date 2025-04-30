"""Find business regulations URL configuration."""

import logging

from rest_framework import routers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

import app.core.views as core_views
import app.search.views as search_views

from app.cache.manage_cache import rebuild_cache
from app.search.utils.documents import document_type_groups
from app.search.utils.search import get_publisher_names, search

urls_logger = logging.getLogger(__name__)


class DataResponseViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request, *args, **kwargs):
        context = {
            "service_name": settings.SERVICE_NAME,
        }

        try:
            response_data = search(context, request)

            # Create a json object from context but exclude paginator
            response_data = {
                "results": response_data["results"],
                "results_count": response_data["results_count"],
                "is_paginated": response_data["is_paginated"],
                "results_total_count": response_data["results_total_count"],
                "results_page_total": response_data["results_page_total"],
                "current_page": response_data["current_page"],
                "start_index": response_data["start_index"],
                "end_index": response_data["end_index"],
            }

            # Return the response
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                data={"message": f"error searching: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DocumentTypesViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="document-types")
    def document_types(self, request, *args, **kwargs):
        try:
            legislation, non_legislation = document_type_groups()

            # Create the response payload
            response_data = {
                "non-legislation": non_legislation,
                "legislation": legislation,
            }

            return Response(
                data=response_data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                data={"message": f"error fetching document types: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PublishersViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="publishers")
    def publishers(self, request, *args, **kwargs):
        try:
            publishers = get_publisher_names()

            results = [
                {
                    "label": item["trimmed_publisher"],
                    "name": item["trimmed_publisher_id"],
                }
                for item in publishers
                if item
                and item.get("trimmed_publisher") is not None
                and item.get("trimmed_publisher_id") is not None
            ]

            return Response(
                data={"results": results},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                data={"message": f"error fetching publishers: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CacheViewSet(viewsets.ViewSet):
    """
    ViewSet for cache-related operations
    """

    @action(detail=False, methods=["POST"])
    def build_cache(self, request):
        """
        Rebuilds the application cache upon receiving a POST request.

        This method triggers the cache rebuilding process and returns the
        result.

        If an exception occurs during the process, it captures the exception
        and returns an error response along with a 500 status code.

        Args:
            request (HttpRequest): Represents the HTTP request object.

        Returns:
            Response: An HTTP response that includes the result of the cache
            rebuild or an error message in case of failure.
        """
        try:
            cache_result = rebuild_cache()

            return Response(cache_result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r"v1", DataResponseViewSet, basename="search")
router.register(r"v1/retrieve", PublishersViewSet, basename="publishers")
router.register(
    r"v1/retrieve", DocumentTypesViewSet, basename="document-types"
)

# Only enable this if you want to rebuild cache as endpoint i.e.
# POST https://127.0.0.1:8000/api/v1/cache/build_cache/
# router.register(r"v1/cache", CacheViewSet, basename="cache")


urlpatterns = [
    path("api/", include(router.urls)),
    path("", search_views.search_react, name="search_react"),
    path("nojs/", search_views.search_django, name="search_django"),
    # This is the URL for downloading the search results in CSV format
    path("download_csv/", search_views.download_csv, name="csvdata"),
    path("nojs/download_csv/", search_views.download_csv, name="csvdata"),
    path("document/<str:id>", search_views.document, name="document"),
    path("feedback/", core_views.feedback_view, name="feedback"),
    path("privacy-notice/", core_views.privacy_notice, name="privacy-notice"),
    path(
        "accessibility-statement/",
        core_views.accessibility_statement,
        name="accessibility-statement",
    ),
    path("cookies/", core_views.cookies, name="cookies"),
    path("disclaimer/", core_views.disclaimer, name="disclaimer"),
    path(
        "set-cookie-banner-preference/",
        core_views.set_cookie_banner_preference,
        name="set-cookie-banner-preference",
    ),
    path(
        "hide-cookie-banner/",
        core_views.hide_cookie_banner,
        name="hide-cookie-banner",
    ),
    path("page-not-found/", core_views.page_not_found, name="page_not_found"),
    path("healthcheck/", core_views.health_check, name="healthcheck"),
]

# Define the custom 404 handler
handler404 = "app.core.views.page_not_found"

if settings.DJANGO_ADMIN:
    urlpatterns.append(path("admin/", admin.site.urls))
