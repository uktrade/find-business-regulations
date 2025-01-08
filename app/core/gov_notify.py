import logging
import uuid

from notifications_python_client.notifications import NotificationsAPIClient

from django.conf import settings

logger = logging.getLogger(__name__)


class EmailSendError(Exception):
    """Email send error exception.

    This class is used to raise exceptions when there is an error
    sending an email via the GovUK Notify service.
    """


def send_email_notification(
    email_address, template_id, personalisation=None, reference=None
) -> dict:
    """Send email notification.

    This function sends an email notification using the GovUK Notify API.

    Note: If successful, the response of the GovUK Notify API is returned
    as a dictionary which includes an 'id' key for the successfully sent email.
    """
    if settings.SUPPRESS_NOTIFY:
        logger.warning(
            "SUPPRESS_NOTIFY detected, suppressing email"
            f" notification to: {email_address}"
        )
        return {"id": str(uuid.uuid4()), "status": "testing"}
    notifications_client = NotificationsAPIClient(
        settings.GOVUK_NOTIFY_API_KEY
    )
    response: dict = notifications_client.send_email_notification(
        email_address=email_address,
        template_id=template_id,
        personalisation=personalisation,
        reference=reference,
    )
    if "id" in response:
        # See docstring
        response["status"] = "delivered"
        return response
    else:
        raise EmailSendError(response)
