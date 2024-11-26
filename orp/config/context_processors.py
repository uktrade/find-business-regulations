from django.conf import settings


def google_tag_manager(request):
    """Context processor to add Google Tag Manager ID to all templates."""
    return {"gtm_id": settings.GOOGLE_ANALYTICS_TAG_MANAGER_ID}
