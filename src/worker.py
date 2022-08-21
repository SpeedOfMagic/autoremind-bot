from datetime import datetime
from enum import Enum

from reminder_dao import Reminder, ReminderDao
from telegram_api import TelegramAdapter
from logging_utils import get_logger, Logger


class WorkerState(Enum):
    EXECUTE_COMMAND = 0
    NEW_NAME = 1
    NEW_TIME = 2
    NEW_PERIOD = 3
    DELETE_ID = 4


class Worker:
    state: WorkerState
    chat_id: int
    telegram_api: TelegramAdapter
    reminder_dao: ReminderDao
    logger: Logger

    name: str
    launch_ts: int

    def __init__(self, chat_id, telegram_api, reminder_dao):
        self.state = WorkerState.EXECUTE_COMMAND
        self.chat_id = chat_id
        self.telegram_api = telegram_api
        self.reminder_dao = reminder_dao
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
        elif self.state == WorkerState.NEW_PERIOD:
            return self.process_new_period(message)
        elif self.state == WorkerState.DELETE_ID:
            return self.process_delete_id(message)
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
        self.state = WorkerState.NEW_PERIOD
        time = datetime.fromisoformat(message['text'].strip())  # FIXME avoid type error
        self.launch_ts = int(time.timestamp())
        self.logger.debug(f'Parsed time as {time}; Unix timestamp is {self.launch_ts}')
        return 'Enter period for your reminder (amount of seconds)'

    def process_new_period(self, message):
        self.state = WorkerState.EXECUTE_COMMAND
        period_ts = int(message['text'].strip())  # FIXME avoid type error
        reminder = Reminder(self.chat_id, self.launch_ts, period_ts, self.name)
        self.reminder_dao.insert_reminder(reminder)
        self.logger.info(f'Created new reminder #{reminder.reminder_id} "{reminder.name}" '
                         f'with launch time {reminder.launch_ts} and period {reminder.period_ts}')
        return f'Done, created new reminder #{reminder.reminder_id} "{reminder.name}"'

    def process_list(self, message):
        self.state = WorkerState.EXECUTE_COMMAND
        return 'Here are your reminders:'

    def process_delete(self, _):
        self.state = WorkerState.DELETE_ID
        return 'Enter id for a reminder to delete:'

    def process_delete_id(self, message):
        self.state = WorkerState.EXECUTE_COMMAND
        return 'Reminder not found))'

    def process_help(self, _):
        self.state = WorkerState.EXECUTE_COMMAND
        return '''/new - Add new reminder
/delete - Delete specific reminder
/list - List all reminders
/start - Print start message
/help - Print all commands'''
