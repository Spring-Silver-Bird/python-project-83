import os
from contextlib import closing

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection(database_url=DATABASE_URL):
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
            SELECT urls.id, urls.name,
            MAX(url_checks.created_at) AS last_check,
            MAX(url_checks.status_code) AS status_code
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            GROUP BY urls.id
            ORDER BY urls.id DESC
        """
        with get_connection(self.db_url) as conn, conn.cursor() as cur:
            cur.execute(sql)
            urls = []
            for url in cur.fetchall():
                urls.append({
                    'id': url['id'],
                    'name': url['name'],
                    'last_check': url['last_check'],
                    'status_code': url['status_code'],
                })
            return urls

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
                if row['h1'] is None:
                    row['h1'] = ''
                if row['title'] is None:
                    row['title'] = ''
                if row['description'] is None:
                    row['description'] = ''
            return url_checks_info

    def get_all_urls_checks(self):
        sql = '''
         SELECT DISTINCT ON (urls.id)
            urls.id AS id,
            urls.name AS name,
            url_checks.created_at AS created_at,
            url_checks.status_code AS status_code
        FROM urls
        LEFT JOIN url_checks ON
            urls.id = url_checks.url_id
        ORDER BY id, created_at DESC;
        '''
        with get_connection(self.db_url) as conn, conn.cursor() as cur:
            cur.execute(sql)
            all_urls_checks = cur.fetchall()
            for row in all_urls_checks:
                if row['created_at'] is None:
                    row['created_at'] = ''
                if row['status_code'] is None:
                    row['status_code'] = ''
            return all_urls_checks

