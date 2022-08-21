import requests
from urllib.parse import urlencode


class TelegramAdapter:
    token: str

    def __init__(self, token: str):
        self.token = token

    def create_url(self, method: str, **kwargs):
        return f'https://api.telegram.org/bot{self.token}/{method}?{urlencode(kwargs)}'

    def get_updates(self, offset: int):
        get_updates_url = self.create_url('getUpdates', offset=offset)
        return requests.get(get_updates_url).json()

    def send_message(self, chat_id: int, text: str):
        send_message_url = self.create_url('sendMessage', chat_id=chat_id, text=text)
        return requests.get(send_message_url)

    def send_scheduled_message(self, chat_id: int, text: str, schedule_date: int):
        send_message_url = self.create_url('sendMessage', chat_id=chat_id, text=text, schedule_date=schedule_date)
        return requests.get(send_message_url)
