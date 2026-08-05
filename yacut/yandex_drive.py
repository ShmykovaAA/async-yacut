import asyncio

import aiohttp

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = (
    f'{API_HOST}{API_VERSION}/disk/resources/upload'
)


async def async_upload_files_to_disk(files, disk_token):
    auth_headers = {'Authorization': f'OAuth {disk_token}'}
    tasks = []
    async with aiohttp.ClientSession() as session:
        for file in files:
            tasks.append(
                asyncio.ensure_future(
                    upload_file_to_disk(
                        session=session,
                        file=file,
                        auth_headers=auth_headers,
                    )
                )
            )
        urls = await asyncio.gather(*tasks)
    return urls


async def upload_file_to_disk(session, file, auth_headers,):
    payload = {
        'path': f'app:/{file.filename}',
        'overwrite': 'true',
    }
    async with session.get(
        REQUEST_UPLOAD_URL,
        headers=auth_headers,
        params=payload,
    ) as response:
        response.raise_for_status()
        response_data = await response.json()
        upload_url = response_data['href']
    file.stream.seek(0)
    file_data = file.read()
    async with session.put(
        upload_url,
        data=file_data,
    ) as response:
        response.raise_for_status()
        download_url = response.headers.get('Location')
    return download_url