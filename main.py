import sqlite3

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# SQLite database file path
DATABASE_FILE = "telegram_vacancies.db"


# Define a function to fetch data from the vacancies table
def fetch_raw_messages():
    """
    Fetches data from the "raw_messages" table in the SQLite database.

    Returns:
    - results (list): List of tuples containing the fetched data.

    """
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    cursor.execute("""
    SELECT rm."id", rm."group_name", rm."date", rm."text", rm."author_nickname"
    FROM raw_messages rm;
    """)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results


# Define a function to fetch data from the raw_messages table
def fetch_vacancies():
    """
    Fetches data from the "vacancies" table in the SQLite database, joining with "raw_messages" table.

    Returns:
    - results (list): List of tuples containing the fetched data.

    """
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    cursor.execute("""
    SELECT v."original_vacancy_text", v."offer_type", v."stack", v."seniority", v."experience", v."english", v."location", v."rate", v."contacts", v."message_id", rm."date"
                 FROM vacancies v
                 INNER JOIN raw_messages rm ON v.message_id = rm.id
    """)

    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results


def get_analytic_english():
    """
    Fetches the count of vacancies for each English proficiency level.

    Returns:
    - count_english (list): List of integers representing the count of vacancies for each English level.

    """
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    count_english = []

    for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        cursor.execute("SELECT COUNT(*) FROM vacancies WHERE english =?", (level,))
        count_level = cursor.fetchone()[0]
        count_english.append(count_level)

    cursor.close()
    connection.close()
    return count_english


def get_analytic_seniority():
    """
    Fetches the count of vacancies for each seniority level.

    Returns:
    - count_seniority (list): List of integers representing the count of vacancies for each seniority level.

    """
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    count_seniority = []

    for level in ["junior", "middle", "senior"]:
        cursor.execute("SELECT COUNT(*) FROM vacancies WHERE seniority =?", (level,))
        count_level = cursor.fetchone()[0]
        count_seniority.append(count_level)

    cursor.close()
    connection.close()
    return count_seniority


def get_analytic_offer_type():
    """
    Fetches the count of vacancies for each offer type.

    Returns:
    - count_offer_type (list): List of integers representing the count of vacancies for each offer type.

    """
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    count_offer_type = []

    for type in ["available", "lookfor"]:
        cursor.execute("SELECT COUNT(*) FROM vacancies WHERE offer_type =?", (type,))
        count_level = cursor.fetchone()[0]
        count_offer_type.append(count_level)

    cursor.close()
    connection.close()
    return count_offer_type


def get_analytic_experience():
    """
    Fetches the count of vacancies for each experience level.

    Returns:
    - count_experience (dict): Dictionary where the key is the experience level and the value is the count of vacancies.

    """
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    count_experience = {}

    for year in range(20):
        cursor.execute("SELECT COUNT(*) FROM vacancies WHERE experience =?", (year,))
        count_years = cursor.fetchone()[0]
        count_experience[year] = count_years

    cursor.close()
    connection.close()
    count_experience = {key: value for key, value in count_experience.items() if value != 0}
    return count_experience


# Define the root route to render the table
@app.get("/")
async def read_vacancies(request: Request):
    """
    Defines the root route to render the vacancies table.

    Args:
    - request (Request): The request object.

    Returns:
    - templates.TemplateResponse: Template response object for rendering the vacancies table.

    """
    # Fetch data from the SQLite database
    raw_messages = fetch_raw_messages()
    vacancies = fetch_vacancies()

    # Render the vacancies table in the frontend using a template
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "raw_messages": raw_messages, "vacancies": vacancies}
    )


# Define the analytics route to render the table
@app.get("/analytics/")
async def analytics_vacancies(request: Request):
    """
    Defines the analytics route to render the vacancies analytics table.

    Args:
    - request (Request): The request object.

    Returns:
    - templates.TemplateResponse: Template response object for rendering the vacancies analytics table.

    """
    # Fetch data from the SQLite database
    vacancies = fetch_vacancies()
    count_english = get_analytic_english()
    count_seniority = get_analytic_seniority()
    count_offer_type = get_analytic_offer_type()
    count_experience = get_analytic_experience()
    print(count_experience)

    # Render the vacancies table in the frontend using a template
    return templates.TemplateResponse(
        "analytics.html",
        {"request": request, "vacancies": vacancies, "count_english": count_english, "count_seniority": count_seniority,
         "count_offer_type": count_offer_type, "count_experience": count_experience}
    )
