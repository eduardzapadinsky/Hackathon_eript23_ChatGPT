"""
https://eript23.hackathon.expert
Gather messages from Telegram groups into the db table.

"""

from telethon import TelegramClient
import sqlite3

from keys import API_ID, API_HASH

# Telegram API
client = TelegramClient('telegram_vacancies', API_ID, API_HASH)


async def insert_messages_from_group(c, conn, group_name):
    """
    Inserts messages from a Telegram group into the raw_messages table.

    Args:
        c (sqlite3.Cursor): SQLite cursor object.
        conn (sqlite3.Connection): SQLite database connection object.
        group_name (str): Name of the Telegram group to retrieve messages from.

    """
    async for message in client.iter_messages(group_name, limit=10000):
        # Check if the message already exists in the database
        c.execute("SELECT id FROM raw_messages WHERE group_id=? AND message_id=?", (message.chat.id, message.id,))
        result = c.fetchone()

        if not result and message.text and str(message.date)[:7] in ["2023-01", "2023-02", "2023-03"]:
            # Save the message to the database
            c.execute(
                """INSERT INTO raw_messages (group_id, group_name, message_id, author_id, author_nickname, date, text) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (message.chat.id,
                 message.chat.title,
                 message.id,
                 message.sender_id,
                 message.sender.username,
                 message.date,
                 message.text))
            conn.commit()


async def retrieve_messages():
    """
    Retrieves messages from Telegram groups and stores them in the database.

    """
    # Set up the database connection
    conn = sqlite3.connect('telegram_vacancies.db')
    c = conn.cursor()

    # Create a table to store messages
    c.execute("""CREATE TABLE IF NOT EXISTS raw_messages
                 (id INTEGER PRIMARY KEY,
                  group_id INTEGER,
                  group_name TEXT,
                  message_id INTEGER,
                  author_id INTEGER,
                  author_nickname TEXT,
                  date TEXT,
                  text TEXT)""")

    # Insert data into db
    group_names = ['OnlyUAoutsource']
    for group_name in group_names:
        await insert_messages_from_group(c, conn, group_name)

    # Close the database connection
    conn.close()

    # Parse messages
    # parse_messages()


def run():
    """
    Runs the process to retrieve and store messages from Telegram groups.

    """
    with client:
        client.loop.run_until_complete(retrieve_messages())


run()
