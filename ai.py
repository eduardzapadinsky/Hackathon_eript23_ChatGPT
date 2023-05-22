"""
https://eript23.hackathon.expert
Parse messages from Telegram groups and save them into the db table.

"""

import re
import sqlite3
import json
from json import JSONDecodeError

from langchain.llms import OpenAI
from langchain import PromptTemplate, LLMChain


def get_messages_from_db():
    """
    Retrieves messages from the 'raw_messages' table in the database.

    Returns:
        List of tuples: Each tuple contains the message ID and text.

    """
    # Set up the database connection
    conn = sqlite3.connect('telegram_vacancies.db')
    c = conn.cursor()

    # Select messages text
    # c.execute("SELECT id, text FROM raw_messages")
    c.execute("SELECT id, text FROM raw_messages WHERE id>1312")
    raw_messages = c.fetchall()

    # Delete the 'vacancies' table if it exists
    # c.execute("DROP TABLE IF EXISTS vacancies")

    # Close the database connection
    conn.close()

    return raw_messages


def insert_message(message_id, c, vacancy):
    """
    Inserts a vacancy message into the 'vacancies' table.

    Args:
        message_id (int): Message ID.
        c (sqlite3.Cursor): SQLite cursor object.
        vacancy (dict): Dictionary containing vacancy information.

    """
    original_vacancy_text = vacancy.get("original vacancy text")
    offer_type = vacancy.get("offer type")
    stack = vacancy.get("title")
    seniority = vacancy.get("seniority")
    experience = vacancy.get("experience")
    english = vacancy.get("english")
    location = vacancy.get("location")
    rate = vacancy.get("rate")
    contacts = vacancy.get("contacts")
    c.execute(
        """INSERT INTO vacancies (
        message_id,
        original_vacancy_text, 
        offer_type, 
        stack, 
        seniority, 
        experience, 
        english, 
        location, 
        rate, 
        contacts
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (message_id,
         original_vacancy_text,
         offer_type,
         stack,
         seniority,
         experience,
         english,
         location,
         rate,
         contacts))


def save_message_to_db(message_id, vacancies):
    """
    Saves a vacancy message and its details into the 'vacancies' table.

    Args:
        message_id (int): Message ID.
        vacancies (dict or list): Dictionary or list of dictionaries containing vacancy information.

    """
    # Set up the database connection
    conn = sqlite3.connect('telegram_vacancies.db')
    c = conn.cursor()

    # Create the 'vacancies' table if it doesn't exist
    c.execute("""CREATE TABLE IF NOT EXISTS vacancies
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      message_id INTEGER,
                      original_vacancy_text TEXT,
                      offer_type TEXT,
                      stack TEXT,
                      seniority TEXT,
                      experience TEXT,
                      english TEXT,
                      location TEXT,
                      rate TEXT,
                      contacts TEXT,
                      FOREIGN KEY (message_id) REFERENCES messages (id))""")

    # Insert the data into the 'vacancies' table
    try:
        if isinstance(vacancies, list):
            for vacancy in vacancies:
                insert_message(message_id, c, vacancy)
        else:
            insert_message(message_id, c, vacancies)
    except Exception:
        print("db Error")

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()


def parse_with_openai(raw_message):
    """
    Parses a raw message using OpenAI language model.

    Args:
        raw_message (str): Raw message text.

    Returns:
        str: Parsed message.

    """

    keywords = [
        "original vacancy text",
        "offer type (available/lookfor)",
        "title (Stack / Programming language / Framework / Technology / Or non-tech)",
        "seniority (junior, middle, senior)",
        "experience (years)",
        "english (intermediate, upper-intermediate, advanced, fluent)",
        "location",
        "rate ($)",
        "contacts (begins with '@')"
    ]

    prompt_q = f"""Check, if there one or more job vacancies. 
    If yes,for each of the job vacancies find values only for this keywords {keywords} in the following text. 
    If there is no value, display empty string. 
    Output(s) as a json with double quotes. 
    If there double quotes, single quotes or apostrophe inside any value, remove them"""

    template = """Question: {question}

    Answer: json"""

    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm = OpenAI(temperature=0, max_tokens=3000)
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    question = prompt_q + raw_message
    response = llm_chain.run(question)

    return response


def parse_messages():
    """
    Parses the messages retrieved from the database.

    """
    raw_data = get_messages_from_db()

    for message_id, raw_messages in raw_data:
        try:
            parsed_message = parse_with_openai(raw_messages)
        except Exception:
            print("OpeaAIError")
        try:
            pattern = r"[\[\{]([\s\S]*)[\]\}]"
            parsed_message = re.search(pattern, parsed_message).group(0)
            parsed_message = re.sub(r'[\\\/]', '|', parsed_message)
            print(parsed_message)
        except Exception:
            print("ReError")

        try:
            # Convert string into objects
            vacancies = json.loads(parsed_message, strict=False)

            # Add messages into db
            save_message_to_db(int(message_id), vacancies)

        except JSONDecodeError:
            print("Error")


parse_messages()
