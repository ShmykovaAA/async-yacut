from flask import flash, redirect, render_template, url_for

from . import app, db
from .constants import RESERVED_SHORT_IDS
from .forms import FilesForm, URLForm
from .models import URLMap
from .units import get_unique_short_id
from .yandex_drive import async_upload_files_to_disk


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()

    if form.validate_on_submit():
        if form.custom_id.data:
            short = form.custom_id.data
            if (
                URLMap.query.filter_by(short=short).first() is not None
                or short in RESERVED_SHORT_IDS
            ):
                flash('Предложенный вариант короткой ссылки уже существует.')
                return redirect(url_for('index_view'))
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
async def files_view():
    form = FilesForm()
    uploaded_files = []
    if form.validate_on_submit():
        files = form.files.data
        download_urls = await async_upload_files_to_disk(
            files=files,
            disk_token=app.config['DISK_TOKEN'],
        )
        uploaded_files = []
        for index, file in enumerate(files):
            download_url = download_urls[index]
            short = get_unique_short_id()

            url_map = URLMap(
                original=download_url,
                short=short,
            )
            db.session.add(url_map)

            uploaded_files.append({
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
        )

    return render_template(
        'files.html',
        form=form,
    )