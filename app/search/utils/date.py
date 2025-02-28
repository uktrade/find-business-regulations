import logging
import re

from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def convert_date_string_to_obj(
    date_str: Optional[str], date_format: str = "%Y-%m-%d"
) -> Optional[str]:
    """
    Converts a date string to a specified date format.
    Supports both "%Y-%m-%d" and "%Y-%m" formats.
    Removes double quotes if present in the string.

    :param date_str: The date string to convert
                    (e.g., '2021-03-01', '2014-11').
    :return: The formatted date string or None if input is invalid.
    """
    if date_str and isinstance(date_str, str):
        if date_str is None:
            return None

        # Remove double quotes and any non-date characters from the string
        date_str = re.sub(r"[^\d-]", "", date_str)

        # Determine the expected format and adjust the string accordingly
        parts = date_str.split("-")
        if len(parts) == 1:  # Handle "YYYY" case
            date_str += "-01-01"
            date_format = "%Y-%m-%d"
        elif len(parts) == 2:  # Handle "YYYY-MM" case
            date_str += "-01"
            date_format = "%Y-%m-%d"
        elif len(parts) == 3:  # Handle "YYYY-MM-DD" case
            date_format = "%Y-%m-%d"

        try:
            date_obj = datetime.strptime(date_str, date_format)
            return date_obj.strftime(date_format)
        except ValueError as e:
            logger.error(f"error converting date string: {e}")
            return None
    return None


def format_partial_date_govuk(date_str):
    if not date_str:
        return ""

    try:
        if len(date_str) == 4:
            # Year only
            return date_str
        elif len(date_str) == 7:
            # Year and month
            date_obj = datetime.strptime(date_str, "%Y-%m")
            return date_obj.strftime("%B %Y")
        elif len(date_str) == 10:
            # Year, month, and day
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%-d %B %Y")
        else:
            return date_str
    except ValueError:
        return date_str
