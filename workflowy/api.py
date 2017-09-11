import os
import requests
from .exceptions import LoginFailedException


WORKFLOWY_URL = 'https://workflowy.com'


def sign_in(email, password):
    info = {'username': email, 'password': password, 'next': ''}
    request = requests.post(WORKFLOWY_URL + '/accounts/login/', data=info)

    if not len(request.history) == 1:
        raise LoginFailedException("Wrong username or password")

    cookies = requests.utils.dict_from_cookiejar(request.history[0].cookies)
    return cookies['sessionid']


def get_data(session_id):
    cookie = {'sessionid': session_id}
    request = requests.post(WORKFLOWY_URL + '/get_initialization_data?client_version=18',
                            cookies=cookie)
    return request.json()["projectTreeData"]["mainProjectTreeInfo"]["rootProjectChildren"]
