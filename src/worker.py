from datetime import datetime
from enum import Enum

from telegram_api import TelegramAdapter
from logging_utils import get_logger, Logger


class WorkerState(Enum):
    EXECUTE_COMMAND = 0
    NEW_NAME = 1
    NEW_TIME = 2
    DELETE_NAME = 3


class Worker:
    state: WorkerState
    chat_id: int
    telegram_api: TelegramAdapter
    logger: Logger

    name: str

    def __init__(self, chat_id, telegram_api):
        self.state = WorkerState.EXECUTE_COMMAND
        self.chat_id = chat_id
        self.telegram_api = telegram_api
        self.logger = get_logger(f'worker_{chat_id}')

    def process_message(self, message):
        if 'text' not in message:
            return 'Sorry, I cannot process messages without text'
        text = message['text'].strip()
        if text.startswith('/start'):
            return self.process_start(message)
        elif text.startswith('/new'):
            return self.process_new(message)
        elif text.startswith('/list'):
            return self.process_list(message)
        elif text.startswith('/delete'):
            return self.process_delete(message)
        elif text.startswith('/help'):
            return self.process_help(message)
        elif self.state == WorkerState.NEW_NAME:
            return self.process_new_name(message)
        elif self.state == WorkerState.NEW_TIME:
            return self.process_new_time(message)
        elif self.state == WorkerState.DELETE_NAME:
            return self.process_delete_name(message)
        else:
            return 'Sorry, I did not parse the command'

    def process_start(self, message):
        self.state = WorkerState.EXECUTE_COMMAND
        return f'Hi, {message["from"]["first_name"]}!\n' + \
               'I will store all your reminders and notify you about them!\n' + \
               'Here is my list of commands:\n' + self.process_help(message)

    def process_new(self, _):
        self.state = WorkerState.NEW_NAME
        return 'Enter name for a new reminder:'

    def process_new_name(self, message):
        self.state = WorkerState.NEW_TIME
        self.name = message['text'].strip()
        return 'Enter time for a first reminder (YYYY-MM-DD HH:MM)'

    def process_new_time(self, message):
        self.state = WorkerState.EXECUTE_COMMAND
        time = datetime.fromisoformat(message['text'].strip())
        unix_timestamp = int(time.timestamp())
        self.logger.debug(f'Parsed time as {time}; Unix timestamp is {unix_timestamp}')

        resp = self.telegram_api.send_scheduled_message(self.chat_id, self.name, unix_timestamp)
        self.logger.info(f'Got response while sending scheduled message: {resp.json()}')

        return 'Ok, reminder added'

    def process_list(self, message):
        self.state = WorkerState.EXECUTE_COMMAND
        return 'Here are your reminders:'

    def process_delete(self, message):
        self.state = WorkerState.DELETE_NAME
        return 'Enter name for a reminder to delete:'

    def process_delete_name(self, message):
        self.state = WorkerState.EXECUTE_COMMAND
        return 'Reminder not found))'

    def process_help(self, _):
        self.state = WorkerState.EXECUTE_COMMAND
        return '''/new - Add new reminder
/delete - Delete specific reminder
/list - List all reminders
/start - Print start message
/help - Print all commands'''
