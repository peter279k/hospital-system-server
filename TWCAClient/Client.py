# Import requests module
import requests

# Import loads funcion
from json import loads

class Client:
    def __init__(self, portal_server):
        self.portal_server = portal_server
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        }

    def login_portal(self, payload):
        url = 'https://midonlinetest.twca.com.tw/IDPortal/Login'
        response = requests.post(url, headers=self.headers, data=payload)

        response_dict = loads(response.text)

        return response_dict
