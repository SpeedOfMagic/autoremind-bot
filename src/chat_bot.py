import traceback
from typing import Dict

from worker import Worker
from telegram_api import TelegramAdapter
from logging_utils import get_logger, Logger


class ChatBot:
    telegram_api: TelegramAdapter
    workers: Dict[int, Worker]
    offset: int
    logger: Logger

    def __init__(self, telegram_api):
        self.telegram_api = telegram_api
        self.workers = {}
        self.offset = 0
        self.logger = get_logger('chat_bot')

    def process_message(self):
        result = self.telegram_api.get_updates(self.offset)
        if len(result['result']) == 0:
            return

        result = result['result'][0]
        message = result['message']
        self.logger.info(f'Received message {message}')
        chat_id = message['chat']['id']
        if chat_id not in self.workers:
            self.workers[chat_id] = Worker(chat_id, self.telegram_api)
        response = self.workers[chat_id].process_message(message)
        self.logger.info(f'Sending response "{response}" to chat {chat_id}')
        self.telegram_api.send_message(chat_id, response)
        self.offset = int(result['update_id']) + 1

    def run(self):
        try:
            self.logger.info('autoremind-bot started')
            while True:
                self.process_message()
        except KeyboardInterrupt:
            self.logger.info('autoremind-bot stopped')
        except Exception:
            self.logger.error(f'An exception has occurred:\n{traceback.format_exc()}')
            raise
