import re

from .constants import (
    RESERVED_SHORT_IDS, CUSTOM_ID_PATTERN, CUSTOM_SHORT_ID_LENGTH
)
from .models import URLMap


def short_id_is_occupied(short_id):
    return (
        short_id in RESERVED_SHORT_IDS
        or URLMap.query.filter_by(short=short_id).first() is not None
    )


def short_id_is_valid(short_id):
    return (
        isinstance(short_id, str)
        and 0 < len(short_id) <= CUSTOM_SHORT_ID_LENGTH
        and re.fullmatch(CUSTOM_ID_PATTERN, short_id) is not None
    )