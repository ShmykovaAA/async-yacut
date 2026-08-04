import os
from urllib.parse import unquote

import requests
from dotenv import load_dotenv

load_dotenv()
DISK_TOKEN = os.environ.get('DISK_TOKEN')


API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'

AUTH_HEADERS = {
    'Authorization': f'OAuth {DISK_TOKEN}'
}


def upload_to_disk(filename):
    payload = {
        'path': f'app:/{filename}',
        'overwrite': True,
    }

    response = requests.get(
        url=REQUEST_UPLOAD_URL,
        headers=AUTH_HEADERS,
        params=payload,
    )
    response.raise_for_status()

    upload_url = response.json()['href']

    with open(filename, 'rb') as file:
        response = requests.put(
            url=upload_url,
            data=file,
        )

    response.raise_for_status()

    location = response.headers.get('Location')

    return location
