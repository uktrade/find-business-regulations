from django.db.models import Case, F, Q, Sum, Value, When


def calculate_score(queryset, search_query):
    """
    Calculate relevance scores for a queryset based on a search query
     and order items.

    This function processes a given queryset and a search query string by
    calculating a relevance score for each entry in the queryset.
    The scoring is performed based on the occurrence of individual terms
    from the search query in three fields of the queryset:
    'title', 'regulatory_topics', and 'description'.

    It leverages Django's ORM capabilities, annotates the queryset with
    the calculated scores, and orders the entries in descending order based
    on these scores.

    Arguments:
        queryset (QuerySet): A Django QuerySet that represents the data
            entries to which the scoring system will be applied.
        search_query (str): A string representing the search term(s) used
            to calculate relevance scores. The search query string is
            split into individual terms for processing.

    Returns:
        QuerySet: The original queryset annotated with scoring fields and
            ordered in descending order of relevance determined by the scores.
    """
    search_terms = search_query.split()

    # Create cases for each field
    title_cases = Case(
        *[
            When(Q(title__icontains=term), then=Value(1))
            for term in search_terms
        ],
        default=Value(0)
    )
    regulatory_topics_cases = Case(
        *[
            When(Q(regulatory_topics__icontains=term), then=Value(1))
            for term in search_terms
        ],
        default=Value(0)
    )
    description_cases = Case(
        *[
            When(Q(description__icontains=term), then=Value(1))
            for term in search_terms
        ],
        default=Value(0)
    )

    # Sum the cases for each field
    title_score = Sum(title_cases)
    regulatory_topics_score = Sum(regulatory_topics_cases)
    description_score = Sum(description_cases)

    # Annotate the queryset with the scores
    queryset = queryset.annotate(
        title_score=title_score,
        regulatory_topics_score=regulatory_topics_score,
        description_score=description_score,
    )

    # Order the queryset by the scores
    queryset = queryset.order_by(
        F("title_score").desc(nulls_last=True),
        F("regulatory_topics_score").desc(nulls_last=True),
        F("description_score").desc(nulls_last=True),
    )

    return queryset
