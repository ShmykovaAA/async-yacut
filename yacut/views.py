import string
from random import random

from flask import abort, flash, redirect, render_template, url_for

from . import app, db
from .forms import URLForm, FilesForm
from .models import URLMap

SHORT_ID_LENGTH = 6
RESERVED_SHORT_IDS = {'files'}


def get_unique_short_id():
    symbols = string.ascii_letters + string.digits

    while True:
        short_id = ''.join(
            random.choice(symbols)
            for _ in range(SHORT_ID_LENGTH)
        )

        if URLMap.query.filter_by(short=short_id).first() is None:
            return short_id
                

@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()
    short_url = None

    if form.validate_on_submit():
        if form.custom_id.data is not None:
            short = form.custom_id.data
            if (
                URLMap.query.filter_by(short=short).first() is not None
                or short in RESERVED_SHORT_IDS
            ):
                flash('Предложенный вариант короткой ссылки уже существует.')
                return render_template('get_short_link.html', form=form)
        else:
            short = get_unique_short_id()
        url = URLMap(
            original=form.original_link.data,
            short=short
        )
        db.session.add(url)
        db.session.commit()

        return render_template(
            'get_short_link.html',
            form=form,
            short_url=url_for(
                'redirect_view',
                short=short,
                _external=True,
            ),
        )

    return render_template(
        'get_short_link.html',
        form=form,
    )


@app.route('/<string:short>')
def redirect_view(short):
    url = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url.original)


@app.route('/files', methods=['GET', 'POST'])
def files_view():
    form = FilesForm()
    uploaded_files = []
    if form.validate_on_submit():
        for file in form.files.data:
            download_url = upload_to_disk(file)
            short = get_unique_short_id()
            url_map = URLMap(
                original=download_url,
                short=short
            )
            db.session.add(url_map)
            uploaded_files = append({
                'filename': file.filename,
                'short_url': url_for(
                    'redirect_view',
                    short=short,
                    _external=True,
                ),
            })
        db.session.commit()
        return render_template(
            'files.html',
            form=form,
            uploaded_files=uploaded_files,
        ),

    return render_template(
        'files.html',
        form=form,
    )