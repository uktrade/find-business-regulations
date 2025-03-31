from django.contrib.postgres.search import SearchRank, SearchVector
from django.db.models import Case, F, FloatField, IntegerField, Value, When


def calculate_score(query_objs, queryset):
    """
    Calculate relevance scores for a queryset based on search queries
    and order items with title matches at the top.

    This function processes a given queryset and SearchQuery objects by
    calculating a relevance score for each entry in the queryset.
    The scoring prioritizes matches in the title field to ensure they
    appear at the top of the results, followed by matches in regulatory_topics
    and description fields.

    Arguments:
        query_objs (list): A list of SearchQuery objects representing the
        search terms.
        queryset (QuerySet): A Django QuerySet that represents the data
            entries to which the scoring system will be applied.

    Returns:
        QuerySet: The original queryset annotated with scoring fields and
            ordered to prioritize title matches first, followed by
            overall relevance.
    """
    # Create search vectors with different weights
    title_vector = SearchVector("title", weight="A")  # Highest weight
    regulatory_topics_vector = SearchVector("regulatory_topics", weight="C")
    description_vector = SearchVector(
        "description", weight="B"
    )  # Higher than topics but lower than title

    # Combine vectors
    search_vector = (
        title_vector + regulatory_topics_vector + description_vector
    )

    # Combine all query objects if there are multiple
    if isinstance(query_objs, list) and len(query_objs) > 1:
        combined_query = query_objs[0]
        for query in query_objs[1:]:
            combined_query = combined_query | query
    else:
        combined_query = (
            query_objs[0] if isinstance(query_objs, list) else query_objs
        )

    # Annotate the queryset with scores
    queryset = queryset.annotate(
        # Calculate SearchRank for different fields
        title_rank=SearchRank(title_vector, combined_query),
        description_rank=SearchRank(description_vector, combined_query),
        regulatory_topics_rank=SearchRank(
            regulatory_topics_vector, combined_query
        ),
        # Overall rank
        overall_rank=SearchRank(search_vector, combined_query),
        # Binary flag for ANY title match (this ensures title matches
        # come first)
        has_title_match=Case(
            When(title_rank__gt=0, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        ),
        # Final combined score that prioritizes title matches first
        final_score=Case(
            # First priority tier: Has title match
            When(
                has_title_match=1,
                # Within this tier, order by title rank first, then
                # by overall rank
                then=F("title_rank") * Value(1000)
                + F("overall_rank") * Value(100)
                + F("description_rank") * Value(10)
                + F("regulatory_topics_rank"),
            ),
            # Second priority tier: No title match
            default=F("overall_rank") * Value(100)
            + F("description_rank") * Value(10)
            + F("regulatory_topics_rank"),
            output_field=FloatField(),
        ),
    )

    # Order by final score, ensuring title matches come first
    return queryset.order_by("-has_title_match", "-final_score")
