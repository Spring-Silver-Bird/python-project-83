import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection(db_url=DATABASE_URL):
    """Establishes and returns a connection to the PostgreSQL database."""
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    return conn


def insert_new_url(domain):
    """Inserts a new URL into the database and returns the ID."""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO urls (name)
            VALUES (%s) RETURNING id;
        """,
        (domain,))
        url_id = cur.fetchone()[0]
        return url_id


def get_existing_urls():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute('SELECT id, name FROM urls')
        return cur.fetchall()


def is_url_existing(conn, domain):
    """Checks if the URL already exists in the database."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id FROM urls WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s));',
                (domain,),
            )
            existing = cur.fetchone()
            if existing:
                flash("Страница уже существует", "info")
                return True
    except Exception as e:
        flash(f"Ошибка при проверке существования"
              f" страницы в базе данных: {str(e)}", "danger")
        return False
    return False