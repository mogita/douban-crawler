from os import environ as env
import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values

log = logging.getLogger(__name__)

db_host = env.get("DB_HOST")
db_user = env.get("DB_USER")
db_pass = env.get("DB_PASS")
db_name = env.get("DB_NAME")

class DB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=db_host, database=db_name, user=db_user, password=db_pass,
        )
        self.cur = self.conn.cursor()

    def get_book_by_id(self, id=""):
        if id == "":
            return None
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """SELECT * FROM public.books WHERE id = %s""",
            (id,),
        )
        return cur.fetchone()

    def get_uncrawled_books(self, batch_count=5):
        if batch_count < 0:
            batch_count = 5
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """SELECT * FROM public.books WHERE crawled = False LIMIT %s""",
            (batch_count,),
        )
        return cur.fetchall()

    def insert_books(self, books=[]):
        if len(books) == 0:
            return None
        execute_values(
            self.cur,
            """INSERT INTO public.books (
                title,
                subtitle,
                author,
                publisher,
                published_at,
                price,
                isbn,
                pages,
                bookbinding,
                book_intro,
                author_intro,
                toc,
                rating,
                rating_count,
                cover_img_url,
                origin,
                origin_id,
                origin_url,
                crawled
            ) VALUES %s
            ON CONFLICT DO NOTHING""",
            books
        )
        self.conn.commit()

    def update_books(self, books=[]):
        if len(books) == 0:
            return None
        execute_values(
            self.cur,
            """UPDATE public.books SET
                title = data.title,
                subtitle = data.subtitle,
                author = data.author,
                publisher = data.publisher,
                published_at = data.published_at,
                price = data.price,
                isbn = data.isbn,
                pages = data.pages,
                bookbinding = data.bookbinding,
                book_intro = data.book_intro,
                author_intro = data.author_intro,
                toc = data.toc,
                rating = data.rating,
                rating_count = data.rating_count,
                cover_img_url = data.cover_img_url,
                origin = data.origin,
                origin_id = data.origin_id,
                origin_url = data.origin_url,
                crawled = data.crawled,
                updated_at = (now() at time zone 'utc')
            FROM (VALUES %s) AS data (
                id,
                title,
                subtitle,
                author,
                publisher,
                published_at,
                price,
                isbn,
                pages,
                bookbinding,
                book_intro,
                author_intro,
                toc,
                rating,
                rating_count,
                cover_img_url,
                origin,
                origin_id,
                origin_url,
                crawled
            ) WHERE books.id = data.id""",
            books
        )
        self.conn.commit()

    def get_tags(self, batch_count=5):
        if batch_count < 0:
            batch_count = 5
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """SELECT * FROM public.tags LIMIT %s""",
            (batch_count,),
        )
        return cur.fetchall()

    def insert_tags(self, tags=[]):
        if len(tags) == 0:
            return None
        execute_values(
            self.cur,
            """INSERT INTO tags (
                name,
                current_page
            ) VALUES %s
            ON CONFLICT DO NOTHING""",
            tags
        )
        self.conn.commit()

    def update_tags(self, tags=[]):
        if len(tags) == 0:
            return None
        log.debug(tags)
        execute_values(
            self.cur,
            """UPDATE public.tags SET
                name = data.name,
                current_page = data.current_page,
                updated_at = (now() at time zone 'utc')
            FROM (VALUES %s) AS data (
                id,
                name,
                current_page
            ) WHERE tags.id = data.id""",
            tags
        )
        self.conn.commit()

    def cursor(self):
        return self.cur

    def conn(self):
        return self.conn

    def close(self):
        if self.conn:
            self.cur.close()
            self.conn.close()

