import string
from random import choices

from .constants import SHORT_ID_LENGTH
from .models import URLMap


def get_unique_short_id():
    symbols = string.ascii_letters + string.digits

    while True:
        short_id = ''.join(
            choices(symbols, k=SHORT_ID_LENGTH)
            for _ in range(SHORT_ID_LENGTH)
        )

        if URLMap.query.filter_by(short=short_id).first() is None:
            return short_id
