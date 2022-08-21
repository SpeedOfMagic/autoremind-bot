import time
import traceback
from typing import Dict

from logging_utils import get_logger, Logger
from worker import Worker
from reminder_dao import ReminderDao
from telegram_api import TelegramAdapter


class ChatBot:
    telegram_api: TelegramAdapter
    reminder_dao: ReminderDao
    workers: Dict[int, Worker]
    offset: int
    logger: Logger

    def __init__(self, telegram_api):
        self.telegram_api = telegram_api
        self.reminder_dao = ReminderDao()
        self.workers = {}
        self.offset = 0
        self.logger = get_logger('chat_bot')

    def process_pending_message(self):
        result = self.telegram_api.get_updates(self.offset)
        if len(result['result']) == 0:
            return

        result = result['result'][0]
        message = result['message']
        self.logger.info(f'Received message {message}')
        chat_id = message['chat']['id']
        if chat_id not in self.workers:
            self.workers[chat_id] = Worker(chat_id, self.telegram_api, self.reminder_dao)
        response = self.workers[chat_id].process_message(message)
        self.logger.info(f'Sending response "{response}" to chat {chat_id}')
        self.telegram_api.send_message(chat_id, response)
        self.offset = int(result['update_id']) + 1

    def process_reminders(self):
        cur_time = int(time.time())
        reminders = self.reminder_dao.get_reminders()
        for reminder in reminders:
            if reminder.launch_ts <= cur_time:
                self.telegram_api.send_message(reminder.chat_id, reminder.name)
                self.reminder_dao.delete_reminder(reminder.reminder_id)

                if reminder.period_ts > 0:  # TODO Make update_reminder func that updates launch_ts and not recreates it
                    while reminder.launch_ts <= cur_time:  # TODO Optimize this
                        reminder.launch_ts += reminder.period_ts
                    self.reminder_dao.insert_reminder(reminder)

    def run(self):
        try:
            self.logger.info('autoremind-bot started')
            while True:
                self.process_reminders()
                self.process_pending_message()
        except KeyboardInterrupt:
            self.logger.info('autoremind-bot stopped')
        except Exception:
            self.logger.error(f'An exception has occurred:\n{traceback.format_exc()}')
            raise
