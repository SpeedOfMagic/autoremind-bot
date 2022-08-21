import argparse
import logging

from telegram_api import TelegramAdapter
from chat_bot import ChatBot


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--telegram-token', required=True, help='Token for Telegram API')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    telegram = TelegramAdapter(args.telegram_token)
    chat_bot = ChatBot(telegram)
    chat_bot.run()
