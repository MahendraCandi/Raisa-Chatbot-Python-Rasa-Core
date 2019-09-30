import configparser
import logging
from datetime import datetime, timedelta

from pathlib import Path
import requests

__config = configparser.ConfigParser()
__p = Path('.').resolve()
__configPath = __p / 'resources' / 'application.config'
__config.read(__configPath)
_token_credential = __config['token.credential']
_api = __config['api']


class API:
    def __init__(self, channel=None):
        self.__token = TokenAPI()
        self.__channel = channel

    def _get_token(self):
        self._print_token_value()
        hit_token = True
        if self._check_token_is_token_api():
            hit_token = self.check_token_is_expired()

        if hit_token is True:
            url_token = _token_credential['URLToken']
            request_body = {
                "client_id": _token_credential['ClientId'],
                "client_secret": _token_credential['ClientSecret'],
                "username": _token_credential['UserName'],
                "password": _token_credential['Password'],
                "grant_type": _token_credential['GrantType']
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            r = requests.post(url_token, request_body, headers)
            data = r.json()
            token_api = TokenAPI()
            token_api.access_token = data['access_token']
            token_api.expires_in = data['expires_in']
            token_api.refresh_expires_in = data['refresh_expires_in']
            token_api.refresh_token = data['refresh_token']
            token_api.token_type = data['token_type']
            timestamp = datetime.now() + timedelta(seconds=600)
            token_api.timestamp = timestamp.timestamp()
            self.__token = token_api
        return self

    def check_token_is_expired(self):
        time_now = datetime.now().timestamp()
        if self.__token.timestamp is None:
            return True
        else:
            if time_now > self.__token.timestamp:
                return True
        return False

    def _check_token_is_token_api(self):
        if isinstance(self.__token, TokenAPI):
            return True
        return False

    @staticmethod
    def _get_timestamp_now():
        return datetime.now().timestamp()

    def _print_token_value(self):
        logging.debug(f'## TOKEN {str(self.__token)}')
        logging.debug(f'## CHANNEL {self.__channel}')

    def get_api_1(self, kontrak, ktp):
        url = _api['url_api_1']
        self._get_token()
        token = self.__token.access_token
        params = {
            'contract_no': kontrak,
            'ident_type': '01',
            'identity_no': ktp
        }
        header = {
            'Authorization': f'bearer {token}'
        }
        r = requests.get(url, params=params, headers=header)
        if r.status_code == 200:
            return r.json()
        else:
            return None

    def get_api_2(self, nomor_kontrak):
        url = _api['url_api_2']
        self._get_token()
        token = self.__token.access_token
        params = {
            'contract_no': nomor_kontrak
        }
        header = {
            'Authorization': f'bearer {token}'
        }
        r = requests.get(url, params=params, headers=header)
        if r.status_code == 200:
            return r.json()
        else:
            return None

    def get_api_3(self, nomor_ktp):
        url = _api['url_api_3']
        self._get_token()
        token = self.__token.access_token
        params = {
            'identity_no': nomor_ktp
        }
        header = {
            'Authorization': f'bearer {token}'
        }
        r = requests.get(url, params=params, headers=header)
        if r.status_code == 200:
            return r.json()
        else:
            return None


class TokenAPI:
    def __init__(self):
        self.access_token = None
        self.expires_in = None
        self.refresh_expires_in = None
        self.refresh_token = None
        self.token_type = None
        self.timestamp = None
