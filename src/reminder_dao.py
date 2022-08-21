from random import randint
import sqlite3
from typing import List


class Reminder:
    reminder_id: int
    chat_id: int
    launch_ts: int
    period_ts: int
    name: str

    def __init__(self, chat_id: int, launch_ts: int, period_ts: int, name: str, reminder_id=None):
        if reminder_id is None:
            reminder_id = randint(0, 2 ** 63 - 1)
        self.reminder_id = reminder_id
        self.chat_id = chat_id
        self.launch_ts = launch_ts
        self.period_ts = period_ts
        self.name = name


class ReminderDao:
    DB_PATH = 'reminders.db'

    def __init__(self):
        connection = sqlite3.connect(self.DB_PATH)
        connection.row_factory = sqlite3.Row

        connection.cursor().execute('''CREATE TABLE IF NOT EXISTS "Reminders" (
            "reminder_id" INTEGER PRIMARY KEY,
            "chat_id" INTEGER NOT NULL,
            "launch_ts" INTEGER NOT NULL,
            "period_ts" INTEGER NOT NULL,
            "name" STRING NOT NULL
        );''')
        connection.commit()

    def insert_reminder(self, reminder: Reminder):
        connection = sqlite3.connect(self.DB_PATH)
        connection.row_factory = sqlite3.Row

        connection.cursor().execute('INSERT INTO Reminders VALUES (?, ?,?,?,?)', (
            reminder.reminder_id, reminder.chat_id, reminder.launch_ts, reminder.period_ts, reminder.name
        ))
        connection.commit()

    def delete_reminder(self, reminder_id: int):
        connection = sqlite3.connect(self.DB_PATH)
        connection.row_factory = sqlite3.Row

        connection.cursor().execute('DELETE FROM Reminders WHERE reminder_id = ?', (reminder_id,))
        connection.commit()

    def get_reminders(self) -> List[Reminder]:
        connection = sqlite3.connect(self.DB_PATH)
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Reminders')
        rows = cursor.fetchall()
        cursor.close()
        return [Reminder(**row) for row in rows]
