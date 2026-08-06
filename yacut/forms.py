from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import (
    URL, DataRequired, Length, Optional, Regexp, ValidationError
)

from .constants import (
    CUSTOM_SHORT_ID_LENGTH, CUSTOM_ID_PATTERN, MIN_CUSTOM_SHORT_ID_LENGTH
)
from .validators import short_id_is_occupied


class URLForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Введите корректный URL'),
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(MIN_CUSTOM_SHORT_ID_LENGTH, CUSTOM_SHORT_ID_LENGTH),
            Regexp(
                CUSTOM_ID_PATTERN,
                message='Используйте только латинские буквы и цифры',
            ),
        ]
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        if field.data and short_id_is_occupied(field.data):
            raise ValidationError(
                'Предложенный вариант короткой ссылки уже существует.'
            )


class FilesForm(FlaskForm):
    files = MultipleFileField(
        validators=[
            FileRequired(message='Обязательное поле'),
        ]
    )
    submit = SubmitField('Загрузить')

