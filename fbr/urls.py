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

from app.search.models import DataResponseModel
from app.search.utils.documents import clear_all_documents
from app.search.utils.search import get_publisher_names, search

urls_logger = logging.getLogger(__name__)


class DataResponseViewSet(viewsets.ModelViewSet):
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request, *args, **kwargs):
        context = {
            "service_name": settings.SERVICE_NAME_SEARCH,
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


class TempCacheDataResponseViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="cache")
    def read_cachetempdata(self, request, *args, **kwargs):
        try:
            from fbr.tempcache import CACHETEMPDATA

            clear_all_documents()

            for record in CACHETEMPDATA:
                DataResponseModel.objects.create(**record)

            return Response(
                {"message": "data inserted successfully"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"message": f"error reading CACHETEMPDATA: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

router.register(r"v1", DataResponseViewSet, basename="search")
router.register(r"v1/retrieve", PublishersViewSet, basename="publishers")
router.register(r"v1/temp", TempCacheDataResponseViewSet, basename="cache")

urlpatterns = [
    path("api/", include(router.urls)),
    path("", search_views.search_react, name="search_react"),
    path("nojs/", search_views.search_django, name="search_django"),
    path("download_csv/", search_views.download_csv, name="csvdata"),
    # If we choose to have a start page with green button, this is it:
    # path("", core_views.home, name="home"),
    path("document/<str:id>", search_views.document, name="document"),
    path("healthcheck/", core_views.health_check, name="healthcheck"),
    path(
        "accessibility-statement/",
        core_views.accessibility_statement,
        name="accessibility-statement",
    ),
    path("privacy-notice/", core_views.privacy_notice, name="privacy-notice"),
    path("cookies/", core_views.cookies, name="cookies"),
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
    path("test-email/", core_views.test_email, name="test-email"),
    # path("search/", orp_views.search, name="search"),
]

if settings.DJANGO_ADMIN:
    urlpatterns.append(path("admin/", admin.site.urls))
