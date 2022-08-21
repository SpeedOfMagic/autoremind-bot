import requests
from urllib.parse import urlencode


class TelegramAdapter:
    token: str

    def __init__(self, token):
        self.token = token

    def create_url(self, method, **kwargs):
        return f'https://api.telegram.org/bot{self.token}/{method}?{urlencode(kwargs)}'

    def get_updates(self, offset):
        get_updates_url = self.create_url('getUpdates', offset=offset)
        return requests.get(get_updates_url).json()

    def send_message(self, chat_id, text):
        send_message_url = self.create_url('sendMessage', chat_id=chat_id, text=text)
        requests.get(send_message_url)
