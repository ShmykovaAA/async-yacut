from flask import jsonify, request, url_for
from http import HTTPStatus

from . import app, db
from .errorhandler import InvalidAPIUsage
from .models import URLMap
from .units import get_unique_short_id
from .validators import short_id_is_occupied, short_id_is_valid


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    url = data.get('url')
    if not isinstance(url, str) or not url:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    short_id = data.get('custom_id')
    if short_id in (None, ''):
        short_id = get_unique_short_id()
    else:
        if not short_id_is_valid(short_id):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки',
                status_code=HTTPStatus.BAD_REQUEST,
            )

        if short_id_is_occupied(short_id):
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.',
                status_code=HTTPStatus.BAD_REQUEST,
            )

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
    }), HTTPStatus.CREATED


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', status_code=404,)
    return jsonify({
        'url': url_map.original,
    }), HTTPStatus.OK