import os
from contextlib import closing

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv('DATABASE_URL')
MAX_DISPLAY_LENGTH = 200


def truncate_text(value: str) -> str:
    if len(value) > MAX_DISPLAY_LENGTH:
        return f'{value[:MAX_DISPLAY_LENGTH]}...'
    return value


def get_connection(database_url=DATABASE_URL):
    if not database_url:
        raise RuntimeError('DATABASE_URL is not set')
    return closing(
        psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    )


class UrlData:
    def __init__(self, db_url):
        self.db_url = db_url

    def insert_new_url(self, url):
        """Inserts a new URL into the database and returns the ID."""
        sql = """
        INSERT INTO urls (name)
        VALUES (%s)
        RETURNING id;
        """
        with get_connection(self.db_url) as conn, conn.cursor() as cur:
            cur.execute(sql, (url,))
            url_id = cur.fetchone()['id']
            conn.commit()
            return url_id

    def find_url(self, url):
        sql = '''
        SELECT id, name
        FROM urls
        WHERE name = %s
        '''
        with get_connection(self.db_url) as conn, conn.cursor() as cur:
            cur.execute(sql, (url,))
            return cur.fetchone()

    def find_id(self, url_id):
        sql = '''
        SELECT *
        FROM urls
        WHERE id = %s
        '''
        with get_connection(self.db_url) as conn, conn.cursor() as cur:
            cur.execute(sql, (url_id,))
            return cur.fetchone()

    def get_url_id(self, name):
        """Fetches the ID of the URL from the database."""
        sql = "SELECT id FROM urls WHERE name = %s;"
        with get_connection(self.db_url) as conn, conn.cursor() as cur:
            cur.execute(sql, (name,))
            row = cur.fetchone()
            return row['id'] if row else None

    def get_url_data(self, url_id):
        sql = "SELECT id, name, created_at FROM urls WHERE id = %s"
        with get_connection(self.db_url) as conn, conn.cursor() as cur:
            cur.execute(sql, (url_id,))
            url_info = cur.fetchone()
            if not url_info:
                return None
            return {
                'id': url_info['id'],
                'name': url_info['name'],
                'created_at': url_info['created_at'],
            }

    def add_url_check(self, data, url_info):
        sql = """
        INSERT INTO url_checks (url_id, status_code, h1, title, description)
        VALUES (%s, %s, %s, %s, %s)
        """
        with get_connection(self.db_url) as conn, conn.cursor() as cur:
            cur.execute(sql, (
                url_info.get('id'),
                data.get('status'),
                data.get('h1'),
                data.get('title'),
                data.get('description'),
            ))
            conn.commit()

    def get_existing_urls(self):
        sql = """
            SELECT * FROM (
                SELECT DISTINCT ON (urls.id)
                    urls.id, urls.name,
                    url_checks.created_at AS last_check,
                    url_checks.status_code
                FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.url_id
                ORDER BY urls.id, url_checks.created_at DESC,
                         url_checks.id DESC
            ) AS sub
            ORDER BY id DESC
        """
        with get_connection(self.db_url) as conn, conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()

    def get_url_checks(self, url_id):
        sql = """
            SELECT id, status_code, title, h1, description, created_at
            FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC
        """
        with get_connection(self.db_url) as conn, conn.cursor() as cur:
            cur.execute(sql, (url_id,))
            url_checks_info = cur.fetchall()
            for row in url_checks_info:
                for field in ('h1', 'title', 'description'):
                    if row[field] is None:
                        row[field] = ''
                    else:
                        row[field] = truncate_text(row[field])
            return url_checks_info
