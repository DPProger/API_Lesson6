import os
import requests
from dotenv import load_dotenv
import random


def delete_comic_files():
    path = os.path.join(os.getcwd(), 'images')
    for the_file in os.listdir(path):
        file_path = os.path.join(path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def generate_random_comic():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    comics_total = response.json()['num']
    return random.randint(1, comics_total)


def fetch_random_xkcd_photo(comic_id):
    path = os.getcwd() + '/' + 'images' + '/'
    os.makedirs(path, mode=0o777, exist_ok=True)
    url = "https://xkcd.com/{}/info.0.json".format(comic_id)
    response = requests.get(url)
    response.raise_for_status()
    link = response.json()['img']
    file_name = '{}xkcd.png'.format(path)
    download_image(link, file_name)


def download_image(url, path):
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)
    file.close()


def get_wall_upload_server(vk_access_token, vk_group_id):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
        'access_token': vk_access_token,
        'v': '5.95',
        'group_id': vk_group_id
    }
    response = requests.get(url, params)
    response.raise_for_status()
    return response.json()['response']


def photo_post(url):
    path = os.getcwd() + '/images/xkcd.png'
    with open(path, 'rb') as image_file_descriptor:
        files = {
            'Content-Type': 'multipart/form-data',
            'photo': image_file_descriptor
        }
        response = requests.post(url, files=files)
        image_file_descriptor.close()
        response.raise_for_status()
        return response.json()


def save_comic_into_album(vk_access_token, vk_group_id, user_id, photo_id, server_id, hash_id):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'access_token': vk_access_token,
        'v': '5.95',
        'user_id': user_id,
        'group_id': vk_group_id,
        'photo': photo_id,
        'server': server_id,
        'hash': hash_id,
        'caption': 'Комикс'
    }
    response = requests.post(url, params)
    response.raise_for_status()
    return response.json()['response']


def public_on_wall(vk_access_token, vk_group_id, media_id, owner_id):
    attachments = 'photo{}_{}'.format(owner_id, media_id)

    url = 'https://api.vk.com/method/wall.post'
    params = {
         'access_token': vk_access_token,
         'v': '5.95',
         'owner_id': '-{}'.format(vk_group_id),
         'friends_only': '0',
         'from_group': '1',
         'message': 'Python comics!!!',
         'attachments': attachments
    }
    response = requests.post(url, params)
    response.raise_for_status()
    return response.json()['response']


if __name__ == "__main__":
    try:
        load_dotenv()
        comic_id = generate_random_comic()
        fetch_random_xkcd_photo(comic_id)

        download_server_id = get_wall_upload_server(os.environ['VK_ACCESS_TOKEN'], os.environ['VK_GROUP_ID'])
        upload_url = download_server_id['upload_url']
        user_id = download_server_id['user_id']

        data_photo_post = photo_post(upload_url)
        photo_id = data_photo_post['photo']
        server_id = data_photo_post['server']
        hash_id = data_photo_post['hash']

        object_photo = save_comic_into_album(os.environ['VK_ACCESS_TOKEN'], os.environ['VK_GROUP_ID'], user_id, photo_id, server_id, hash_id)
        for element in object_photo:
             media_id = element['id']
             owner_id = element['owner_id']
             public_on_wall(os.environ['VK_ACCESS_TOKEN'], os.environ['VK_GROUP_ID'], media_id, owner_id)
        delete_comic_files()
    except requests.exceptions.HTTPError as error:
        exit("Can't get data from server:\n{0}".format(error))


