import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection(db_url=DATABASE_URL):
    """Establishes and returns a connection to the PostgreSQL database."""
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    print('connection to the PostgreSQL database')
    return conn


def insert_new_url(url):
    """Inserts a new URL into the database and returns the ID."""
    sql = "INSERT INTO urls (name) VALUES (%s) RETURNING id;"
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (url,))
        url_id = cur.fetchone()[0]
        return url_id


def get_existing_urls() -> object:
    sql = """
                SELECT urls.id, urls.name,
                MAX(url_checks.created_at) AS last_check,
                MAX(url_checks.status_code) AS status_code
                FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.url_id
                GROUP BY urls.id
                ORDER BY urls.id DESC
                """
    with get_connection() as conn, conn.cursor() as cur:
        urls = []
        cur.execute(sql)
        for url in cur.fetchall():
            urls.append({
                'id': url[0],
                'name': url[1],
                'created_at': url[2]
            })

        return urls

def get_url_data(url_id):
    sql = "SELECT id, name, created_at FROM urls WHERE id = %s"
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (url_id,))
        url_info = cur.fetchone()
        url = {
            'id': url_info[0],
            'name': url_info[1],
            'created_at': url_info[2]
        }
        if not url_info:
            return None
        return url


def add_url_checks(url_id):
    sql = """
    INSERT INTO urls_checks (url_id) VALUES (%s) RETURNING id;
    """
    status_code = 200
    h1 = 'text1'
    title = 'text2'
    description_tag = 'text3'

    print('Try to post url checks...')
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (url_id,))
        url_id = cur.fetchone()[0]
        return url_id

        
def get_url_checks(url_id):
    print('Try to get checks...')
    sql = """
        SELECT id, created_at 
        FROM url_checks 
        WHERE url_id = %s 
        ORDER BY id DESC
        """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (url_id,))
        checks = []
        for check_row in cur.fetchall():
            checks.append({
                'id': check_row[0],
                'created_at': check_row[1]
            })
        return checks

def get_url_id(name):
    """Fetches the ID of the URL from the database."""
    sql = "SELECT id FROM urls WHERE name = %s;"
    print('Try to get url id...')
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (name,))
        url_id = cur.fetchone()[0] or {}
        return url_id


def is_url_existing(url):
    """Checks if the URL already exists in the database."""
    sql = "SELECT id FROM urls WHERE name=%s;"
    print('Try to get urls...')
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (url,))
        existing = cur.fetchone()
        if existing:
            return True
        return False
