import re

from flask import jsonify, request, url_for

from . import app, db
from .constants import (CUSTOM_ID_PATTERN, CUSTOM_SHORT_ID_LENGTH,
                        RESERVED_SHORT_IDS)
from .errorhandler import InvalidAPIUsage
from .models import URLMap
from .units import get_unique_short_id


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage(
            'Отсутствует тело запроса'
        )
    url = data.get('url')
    if not isinstance(url, str) or not url:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    custom_id = data.get('custom_id')
    if custom_id:
        if (
            len(custom_id) > CUSTOM_SHORT_ID_LENGTH
            or not re.fullmatch(CUSTOM_ID_PATTERN, custom_id)
            or custom_id in RESERVED_SHORT_IDS
        ):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
        if URLMap.query.filter_by(short=custom_id).first() is not None:
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )
        short_id = custom_id
    else:
        short_id = get_unique_short_id()

    url_map = URLMap(
        original=url,
        short=short_id,
    )

    db.session.add(url_map)
    db.session.commit()

    return jsonify({
        'url': url_map.original,
        'short_link': url_for(
            'redirect_view',
            short=url_map.short,
            _external=True,
        ),
    }), 201


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', status_code=404,)
    return jsonify({
        'url': url_map.original,
    }), 200