import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SMSService:

    @staticmethod
    def send_sms(
        recipient: str,
        message: str,
    ) -> bool:

        if not recipient:
            logger.warning(
                "SMS not sent: recipient is empty"
            )
            return False

        try:

            response = requests.get(
                settings.SMS_API_URL,
                params={
                    "project": settings.SMS_PROJECT,
                    "recipient": recipient,
                    "message": message,
                },
                timeout=15,
            )

            response.raise_for_status()

            logger.info(
                "SMS sent to %s: %s",
                recipient,
                response.text,
            )

            return True

        except requests.RequestException as error:

            logger.error(
                "SMS failed to %s: %s",
                recipient,
                error,
            )

            return False