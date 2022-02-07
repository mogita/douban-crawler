"""
Douban Crawler is a dead siple crawler for data scraping
Copyright (C) 2022 mogita <me@mogita.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
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
        self.connection = psycopg2.connect(
            host=db_host, database=db_name, user=db_user, password=db_pass,
        )

    def get_book_by_id(self, id=""):
        if id == "":
            return None
        cur = self.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """SELECT * FROM public.books WHERE id = %s""",
            (id,),
        )
        return cur.fetchone()

    def get_uncrawled_books(self, batch_count=5, cur=None):
        if cur == None:
            cur = self.cursor(cursor_factory=RealDictCursor)
        if batch_count < 0:
            batch_count = 5
        cur.execute(
            """SELECT * FROM public.books WHERE crawled = false""",
        )
        return cur.fetchmany(size=batch_count)

    def insert_books(self, books=[]):
        if len(books) == 0:
            return None
        execute_values(
            self.cursor(),
            """INSERT INTO public.books (
                title,
                subtitle,
                author,
                author_url,
                author_intro,
                publisher,
                published_at,
                original_title,
                translator,
                producer,
                series,
                price,
                isbn,
                pages,
                bookbinding,
                book_intro,
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
        self.connection.commit()

    def update_books_by_url(self, books=[]):
        if len(books) == 0:
            return None
        execute_values(
            self.cursor(),
            """UPDATE public.books SET
                title = data.title,
                subtitle = data.subtitle,
                author = data.author,
                author_url = data.author_url,
                author_intro = data.author_intro,
                publisher = data.publisher,
                published_at = to_timestamp(data.published_at::int),
                original_title = data.original_title,
                translator = data.translator,
                producer = data.producer,
                series = data.series,
                price = data.price,
                isbn = data.isbn,
                pages = data.pages,
                bookbinding = data.bookbinding,
                book_intro = data.book_intro,
                toc = data.toc,
                rating = data.rating,
                rating_count = data.rating_count,
                cover_img_url = data.cover_img_url,
                origin = data.origin,
                origin_id = data.origin_id,
                crawled = true,
                updated_at = (now() at time zone 'utc')
            FROM (VALUES %s) AS data (
                title,
                subtitle,
                author,
                author_url,
                author_intro,
                publisher,
                published_at,
                original_title,
                translator,
                producer,
                series,
                price,
                isbn,
                pages,
                bookbinding,
                book_intro,
                toc,
                rating,
                rating_count,
                cover_img_url,
                origin,
                origin_id,
                origin_url,
                crawled
            ) WHERE books.origin_url = data.origin_url""",
            books
        )
        self.connection.commit()

    def get_tags(self, batch_count=None):
        query = "SELECT * FROM public.tags WHERE exhausted_t = FALSE OR exhausted_r = FALSE OR exhausted_s = FALSE ORDER BY id"
        if batch_count != None:
            if batch_count <= 0:
                batch_count = 5
            query += f" LIMIT {batch_count}"

        cur = self.cursor(cursor_factory=RealDictCursor)
        cur.execute(query)
        return cur.fetchall()

    def insert_tags(self, tags=[]):
        if len(tags) == 0:
            return None
        execute_values(
            self.cursor(),
            """INSERT INTO tags (
                name,
                current_page_t,
                current_page_r,
                current_page_s,
                exhausted_t,
                exhausted_r,
                exhausted_s
            ) VALUES %s
            ON CONFLICT DO NOTHING""",
            tags
        )
        self.connection.commit()

    def update_tags(self, tags=[]):
        if len(tags) == 0:
            return None
        log.debug(tags)
        execute_values(
            self.cursor(),
            """UPDATE public.tags SET
                name = data.name,
                current_page_t = data.current_page_t,
                current_page_r = data.current_page_r,
                current_page_s = data.current_page_s,
                exhausted_t = data.exhausted_t,
                exhausted_r = data.exhausted_r,
                exhausted_s = data.exhausted_s,
                updated_at = (now() at time zone 'utc')
            FROM (VALUES %s) AS data (
                id,
                name,
                current_page_t,
                current_page_r,
                current_page_s,
                exhausted_t,
                exhausted_r,
                exhausted_s
            ) WHERE tags.id = data.id""",
            tags
        )
        self.connection.commit()

    def get_doulists(self, batch_count=None):
        query = "SELECT * FROM public.doulists WHERE exhausted =FALSE ORDER BY id"
        if batch_count != None:
            if batch_count <= 0:
                batch_count = 5
            query += f" LIMIT {batch_count}"

        cur = self.cursor(cursor_factory=RealDictCursor)
        cur.execute(query)
        return cur.fetchall()

    def insert_doulists(self, doulists=[]):
        if len(doulists) == 0:
            return None
        execute_values(
            self.cursor(),
            """INSERT INTO doulists (
                list_id,
                current_page,
                exhausted
            ) VALUES %s
            ON CONFLICT DO NOTHING""",
            doulists
        )
        self.connection.commit()

    def update_doulists(self, doulists=[]):
        if len(doulists) == 0:
            return None
        execute_values(
            self.cursor(),
            """UPDATE public.doulists SET
                list_id = data.list_id,
                current_page = data.current_page,
                exhausted = data.exhausted,
                updated_at = (now() at time zone 'utc')
            FROM (VALUES %s) AS data (
                id,
                list_id,
                current_page,
                exhausted
            ) WHERE doulists.id = data.id""",
            doulists
        )
        self.connection.commit()

    def cursor(self, name=None, cursor_factory=RealDictCursor):
        return self.connection.cursor(name=name, cursor_factory=cursor_factory)

    def conn(self):
        return self.connection

    def rollback(self):
        return self.connection.rollback()

    def close(self):
        if self.connection:
            self.connection.close()

