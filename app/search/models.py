import logging

from django.db import models

logger = logging.getLogger(__name__)


class DataResponseModel(models.Model):
    """
    DataResponseModel

    A Django model representing various metadata fields related to data
    responses.

    Attributes:
        title: Title of the data response.
        identifier: Unique identifier for the data response.
        publisher: Entity that published the data response.
        publisher_id: Unique ID of the publisher.
        language: Language in which the data response is published.
        format: Format of the data response.
        description: Brief description of the data response.
        date_issued: Date when the data response was issued.
        date_modified: Date when the data response was last modified.
        date_valid: Validity date of the data response as text.
        sort_date: Date used for sorting the data responses.
        audience: Intended audience for the data response.
        coverage: Coverage details of the data response.
        subject: Subject matter of the data response.
        type: Type of the data response.
        license: Licensing information of the data response.
        regulatory_topics: Topics covered by the data response.
        status: Current status of the data response.
        date_uploaded_to_orp: Date when the data response was uploaded to ORP.
        has_format: Format details that the data response has.
        is_format_of:
            Indicates if the data response is a format of another resource.
        has_version: Version details that the data response has.
        is_version_of:
            Indicates if the data response is a version of another resource.
        references: References cited in the data response.
        is_referenced_by:
            Indicates if the data response is referenced by another resource.
        has_part: Part details that the data response has.
        is_part_of:
            Indicates if the data response is a part of another resource.
        is_replaced_by:
            Indicates if the data response is replaced by another resource.
        replaces: Indicates if the data response replaces another resource.
        related_legislation: Related legislation details for the data response.
        id: Primary key of the data response.
    """

    title = models.TextField(null=True, blank=True)
    identifier = models.TextField(null=True, blank=True)
    publisher = models.TextField(null=True, blank=True)
    publisher_id = models.TextField(null=True, blank=True)
    language = models.TextField(null=True, blank=True)
    format = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    date_issued = models.DateField(null=True, blank=True)
    date_modified = models.DateField(null=True, blank=True)
    date_valid = models.TextField(null=True, blank=True)
    source_date_issued = models.TextField(null=True, blank=True)
    source_date_modified = models.TextField(null=True, blank=True)
    source_date_valid = models.TextField(null=True, blank=True)
    sort_date = models.DateField(null=True, blank=True)
    audience = models.TextField(null=True, blank=True)
    coverage = models.TextField(null=True, blank=True)
    subject = models.TextField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    license = models.TextField(null=True, blank=True)
    regulatory_topics = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    date_uploaded_to_orp = models.DateField(null=True, blank=True)
    has_format = models.TextField(null=True, blank=True)
    is_format_of = models.TextField(null=True, blank=True)
    has_version = models.TextField(null=True, blank=True)
    is_version_of = models.TextField(null=True, blank=True)
    references = models.TextField(null=True, blank=True)
    is_referenced_by = models.TextField(null=True, blank=True)
    has_part = models.TextField(null=True, blank=True)
    is_part_of = models.TextField(null=True, blank=True)
    is_replaced_by = models.TextField(null=True, blank=True)
    replaces = models.TextField(null=True, blank=True)
    related_legislation = models.TextField(null=True, blank=True)
    id = models.TextField(primary_key=True)
