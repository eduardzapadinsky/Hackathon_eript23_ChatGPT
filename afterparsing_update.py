"""
https://eript23.hackathon.expert
Afterparsing update messages from db table.

"""

import re
import sqlite3


def update_experience():
    """
    Updates the "experience" column in the "vacancies" table with extracted integer values.

    """
    # Set up the database connection
    conn = sqlite3.connect('telegram_vacancies.db')
    c = conn.cursor()

    # Update the "experience" column in the "vacancies" table
    c.execute("""SELECT id, experience FROM vacancies""")
    rows = c.fetchall()

    for row in rows:
        vacancy_id, experience = row
        if experience:
            pattern = r"^\D*(\d+)"
            match = re.search(pattern, experience)
            if match:
                experience = match.group(1)

                # Update the "experience" column with the extracted integer value
                c.execute("""UPDATE vacancies SET experience = ? WHERE id = ?""", (experience, vacancy_id))

    # Commit the changes to the database
    conn.commit()

    # Close the database connection
    conn.close()


def update_rate():
    """
    Updates the "rate" column in the "vacancies" table with extracted integer values.

    """
    # Set up the database connection
    conn = sqlite3.connect('telegram_vacancies.db')
    c = conn.cursor()

    c.execute("""SELECT id, rate FROM vacancies""")
    rows = c.fetchall()

    for row in rows:
        vacancy_id, rate = row
        if rate:
            pattern = r"^\D*(\d+)"
            match = re.search(pattern, rate)
            if match:
                rate = match.group(1)

                # Update the "experience" column with the extracted integer value
                c.execute("""UPDATE vacancies SET rate = ? WHERE id = ?""", (rate, vacancy_id))

    # Commit the changes to the database
    conn.commit()

    # Close the database connection
    conn.close()


def update_english():
    """
    Updates the "english" column in the "vacancies" table with standardized English proficiency levels.

    """
    # Set up the database connection
    conn = sqlite3.connect('telegram_vacancies.db')
    c = conn.cursor()

    c.execute("""SELECT id, english FROM vacancies""")
    rows = c.fetchall()

    for row in rows:
        vacancy_id, english = row
        if english:
            english = english.lower()
            if "pre" in english or "a2" in english or "english" in english or "convers" in english:
                english = "A2"
            elif "upper" in english or "fluent" in english or "written" in english or "high" in english:
                english = "B2"
            elif "pre" in english:
                english = "A2"
            elif "b1" in english or "inter" in english or "good" in english:
                english = "B1"
            elif "b2" in english:
                english = "B2"
            elif "adv" in english or "c1" in english:
                english = "C1"
            elif "element" in english:
                english = "A1"

            # Update the "experience" column with the extracted integer value
            c.execute("""UPDATE vacancies SET english = ? WHERE id = ?""", (english, vacancy_id))

    # Commit the changes to the database
    conn.commit()

    # Close the database connection
    conn.close()


def update_seniority():
    """
    Updates the "seniority" column in the "vacancies" table with standardized seniority levels.

    """
    # Set up the database connection
    conn = sqlite3.connect('telegram_vacancies.db')
    c = conn.cursor()

    c.execute("""SELECT id, seniority FROM vacancies""")
    rows = c.fetchall()

    for row in rows:
        vacancy_id, seniority = row
        if seniority:
            seniority = seniority.lower()
            if "junior" in seniority:
                seniority = "junior"
            elif "middle" in seniority:
                seniority = "middle"
            elif "senior" in seniority:
                seniority = "senior"
            else:
                seniority = ""

            # Update the "experience" column with the extracted integer value
            c.execute("""UPDATE vacancies SET seniority = ? WHERE id = ?""", (seniority, vacancy_id))

    # Commit the changes to the database
    conn.commit()

    # Close the database connection
    conn.close()


# Call the function to update the "vacancies" table
# update_experience()
#
# update_rate()
# update_english()
# update_seniority()

