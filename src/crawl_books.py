"""
Douban Crawler is a dead siple crawler for data scraping
Copyright (C) 2022 mogita <me@mogita.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
import re
import csv
import time
import argparse
import logging
import requests
from datetime import datetime
from os import path, environ as env
from dotenv import load_dotenv
from urllib.parse import quote, urlsplit
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from src.http import req
from src.proxy_pool import get_count
from src.db import DB
from src.model import book_model

log = logging.getLogger(__name__)

load_dotenv()
BATCH_SIZE = env.get("BATCH_SIZE", 3)


def parse(source, url):
    if source == None:
        return None

    soup = BeautifulSoup(source, 'html.parser')

    url_parts = urlsplit(url)
    path_parts = url_parts.path.split("/")
    douban_book_id = path_parts[2]

    book_meta = soup.select('#info')
    if not book_meta:
        return None

    # Raw meta list with characters like "\n" and continuous spaces
    meta_list_raw = list(book_meta[0].strings)
    # Remove white chars around each element
    meta_list_raw = [i.strip() for i in meta_list_raw if i.strip() != '']

    # Move dangling ":" characters to their previous elements
    # to keep a form of ["label1:", "content1", "content2", "label2:", "content3", ...]
    meta_list_colon_aligned = []
    for idx, val in enumerate(meta_list_raw):
        if val == ":" and len(meta_list_colon_aligned) > 0:
            meta_list_colon_aligned[len(meta_list_colon_aligned) - 1] += val
        else:
            meta_list_colon_aligned.append(val)

    # Concatenate contents separated into multiple elements
    # to keep a form of ["label1:", "content1 content2", "label2:", "content3", ...]
    meta_list = []
    holder = []
    for val in meta_list_colon_aligned:
        if val.endswith(":"):
            if len(holder) > 0:
                meta_list.append(" ".join(holder))
            holder = []
            meta_list.append(val)
        else:
            holder.append(val)
    meta_list.append(" ".join(holder))

    # Remove white characters and continuous spaces inside each element
    meta_list = list(map(lambda r: r.replace("\n", ""), meta_list))
    meta_list = list(map(lambda r: re.sub(' +', ' ', r), meta_list))

    douban_url = url

    # Parsing a bunch of meta info
    title = ""
    title_el = soup.select("#wrapper > h1 > span")
    if title_el:
        title = title_el[0].contents[0]

    subtitle = meta_list[meta_list.index("副标题:") + 1] if "副标题:" in meta_list else ""
    author = meta_list[meta_list.index("作者:") + 1] if "作者:" in meta_list else ""

    author_url = ""
    if soup.select("#info > span > a"):
        # Try the structure of "#info > span > a"
        author_url = soup.select("#info > span > a")[0].attrs["href"]
    elif soup.select("#info > span"):
        # Or try the structure of "#info > span -> first sibling that is an 'a' tag"
        author_el = soup.select("#info > span")[0].find_next("a")
        author_url = author_el.attrs["href"]

    original_title = meta_list[meta_list.index('原作名:') + 1] if '原作名:' in meta_list else ''
    translator = meta_list[meta_list.index('译者:') + 1] if '译者:' in meta_list else ''

    producer = meta_list[meta_list.index('出品方:') + 1] if '出品方:' in meta_list else ''
    series = meta_list[meta_list.index('丛书:') + 1] if '丛书:' in meta_list else ''

    price = meta_list[meta_list.index('定价:') + 1] if '定价:' in meta_list else ''
    isbn = meta_list[meta_list.index('ISBN:') + 1]  if 'ISBN:' in meta_list else ''
    pages = meta_list[meta_list.index('页数:') + 1] if '页数:' in meta_list else '0'
    bookbinding = meta_list[meta_list.index('装帧:') + 1] if '装帧:' in meta_list else ''

    publisher = meta_list[meta_list.index('出版社:') + 1] if '出版社:' in meta_list else ''
    published_at = meta_list[meta_list.index('出版年:') + 1] if '出版年:' in meta_list else ''

    # convert "published_at" into a valid timestamp
    published_at_ts = None
    if published_at != "":
        try:
            # Some(times) are represented as 10/8/2003
            if published_at.count("/") == 2:
                parts = published_at.split("/")
                # Guess if last position is year, and swap to the first in the list
                if len(parts) > 2 and int(parts[0]) < int(parts[2]):
                    parts.insert(0, parts[2])
                    del parts[3]
                published_at = "-".join(parts)
            # Some(times) are represented as 2018.12 so we need to align the format first
            published_at = published_at.replace(".", "-")
            # Some(times) are represented as 2018年4月
            published_at = published_at.replace("年", "-")
            published_at = published_at.replace("月", "-")
            published_at = published_at.replace("日", "-")
            if published_at.endswith("-"):
                published_at = published_at[:-1]

            published_at_split = published_at.split("-")
            published_at_ts = datetime(
                int(published_at_split[0] if len(published_at_split) >= 1 else "2"),
                int(published_at_split[1] if len(published_at_split) >= 2 else "1"),
                int(published_at_split[2] if len(published_at_split) >= 3 else "1"),
            ).timestamp()
            published_at_ts = int(round(published_at_ts))
        except Exception as err:
            log.warn("failed to parse published_at to timestamp")
            log.warn(err)

    # Parsing 内容简介 (book introduction)
    book_intro_el = soup.select("#link-report")
    book_intro = ""
    if book_intro_el:
        if book_intro_el[0].select("span.short") and book_intro_el[0].select("span.all"):
            book_intro = book_intro_el[0].select(".intro")[1].contents
        else:
            book_intro = book_intro_el[0].select(".intro")[0].contents
        book_intro = list(map(lambda line: str(line), book_intro))
        book_intro = "".join(filter(lambda line: line != "\n" and line != " ", book_intro)).strip()

    # Parsing 作者简介 (author introduction)
    author_title_el = soup.find("span", string="作者简介")
    author_intro = ""
    if author_title_el:
        author_intro_el = author_title_el.parent.find_next('div', {'class': 'indent'})
        if author_intro_el.select("span.short") and author_intro_el.select("span.all"):
            author_intro = author_intro_el.select("span.all > .intro")[0].contents
        else:
            author_intro = author_intro_el.select(".intro")[0].contents
    author_intro = list(map(lambda line: str(line), author_intro))
    author_intro = "".join(filter(lambda line: line != "\n" and line != " ", author_intro)).strip()

    # Parsing table of contents
    toc_el = soup.select(f"#dir_{douban_book_id}_full")
    toc_parts = toc_el[0].get_text().split("\n") if toc_el else []
    toc_parts = list(filter(lambda row: row != "", toc_parts))
    if len(toc_parts) > 0 and  '(收起)' in toc_parts[len(toc_parts) - 1]:
        toc_parts.pop()
    toc = "<br />".join(map(lambda line: line.replace("\u3000", " ").replace("\t", " ").strip(), toc_parts))

    # Parsing ratings
    rating_el = soup.select("#interest_sectl > div > div.rating_self.clearfix > strong")
    rating = rating_el[0].contents[0].strip() if rating_el else "0"
    if rating == "":
        rating = "0"

    rating_count_el = soup.select("#interest_sectl > div > div.rating_self.clearfix > div > div.rating_sum > span > a > span")
    rating_count = rating_count_el[0].contents[0] if rating_count_el else "0"
    if rating_count == "":
        rating_count = "0"

    # Parsing cover image
    cover_img_url = soup.select("#mainpic > a > img")[0].attrs["src"]

    # Parsing "recommendation" section for more book links
    recmd_books = []
    recmd_el = soup.find("div", {"id": "db-rec-section"})
    if recmd_el != None:
        recmd_books = list(map(lambda r: parse_recmd_books(r), recmd_el.select("dl")))
        recmd_books = list(filter(lambda r: r != None, recmd_books))

    return (book_model({
        'title': title,
        'subtitle': subtitle,
        'author': author,
        'author_url': author_url,
        'author_intro': author_intro,
        'publisher': publisher,
        'published_at': published_at_ts,
        'original_title': original_title,
        'translator': translator,
        'producer': producer,
        'series': series,
        'price': price,
        'isbn': isbn,
        'pages': pages,
        'bookbinding': bookbinding,
        'book_intro': book_intro,
        'toc': toc,
        'rating': float(rating),
        'rating_count': int(rating_count),
        'cover_img_url': cover_img_url,
        'origin': 'douban',
        'origin_id': douban_book_id,
        'origin_url': douban_url,
        'crawled': True,
    }), recmd_books)


def parse_recmd_books(el):
    link = ""
    try:
        link = el.select("dt > a")[0].attrs["href"]
    except:
        try:
            link = el.select("dd > a")[0].attrs["href"]
        except:
            pass
    if link != "":
        return book_model({ 'origin_url': link })
    else:
        return None


def flatten(t):
    return [item for sublist in t for item in sublist]


def _start(args):
    db_iterator = DB()
    db_updater = DB()
    db_inserter = DB()
    with db_iterator.cursor(name="book_links") as cur:
        query = "SELECT * FROM books WHERE crawled = false"
        cur.execute(query)

        while True:
            books_data = cur.fetchmany(size=int(BATCH_SIZE))
            if not books_data:
                log.info("no uncrawled books in database")
                break
            links = list(map(lambda r: r['origin_url'], books_data))
            with ThreadPoolExecutor() as tpool:
                log.info(f"requesting {len(links)} links...")
                response_list = list(tpool.map(req, links))
                log.info(f"parsing {len(response_list)} responses...")
                parse_res = list(tpool.map(lambda r: parse(r[0], r[1]), response_list))
                parse_res = list(filter(lambda r: r != None, parse_res))

                books_data = list(map(lambda r: r[0], parse_res))
                books_data = list(filter(lambda r: r != None, books_data))
                log.info(f"parsed {len(books_data)} books")

                recmd_books = flatten(list(map(lambda r: r[1], parse_res)))
                log.info(f"found {len(recmd_books)} books from recommendation section")

            try:
                db_updater.update_books_by_url(books_data)
                log.info(f"updated {len(books_data)} books")
            except Exception as err:
                db_updater.rollback()
                log.error("failed to update books")
                log.error(err)

            try:
                db_inserter.insert_books(recmd_books)
                log.info(f"saved {len(recmd_books)} books from recommendation section")
            except Exception as err:
                db_inserter.rollback()
                log.error(f"failed to save books from recommendation section")
                log.error(err)

            time.sleep(np.random.rand()*5)

def main(raw_args=None):
    parser = argparse.ArgumentParser(
        description="Crawl book information from douban.com from a given list of links."
    )
    args = parser.parse_args(raw_args)

    _start(args)


if __name__ == "__main__":
    main()
