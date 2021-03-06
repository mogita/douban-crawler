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

    subtitle = meta_list[meta_list.index("?????????:") + 1] if "?????????:" in meta_list else ""
    author = meta_list[meta_list.index("??????:") + 1] if "??????:" in meta_list else ""

    author_url = ""
    if soup.select("#info > span > a"):
        # Try the structure of "#info > span > a"
        author_url = soup.select("#info > span > a")[0].attrs["href"]
    elif soup.select("#info > span"):
        # Or try the structure of "#info > span -> first sibling that is an 'a' tag"
        author_el = soup.select("#info > span")[0].find_next("a")
        author_url = author_el.attrs["href"]

    original_title = meta_list[meta_list.index('?????????:') + 1] if '?????????:' in meta_list else ''
    translator = meta_list[meta_list.index('??????:') + 1] if '??????:' in meta_list else ''

    producer = meta_list[meta_list.index('?????????:') + 1] if '?????????:' in meta_list else ''
    series = meta_list[meta_list.index('??????:') + 1] if '??????:' in meta_list else ''

    price = meta_list[meta_list.index('??????:') + 1] if '??????:' in meta_list else ''
    isbn = meta_list[meta_list.index('ISBN:') + 1]  if 'ISBN:' in meta_list else ''
    pages = meta_list[meta_list.index('??????:') + 1] if '??????:' in meta_list else '0'
    bookbinding = meta_list[meta_list.index('??????:') + 1] if '??????:' in meta_list else ''

    publisher = meta_list[meta_list.index('?????????:') + 1] if '?????????:' in meta_list else ''
    published_at = meta_list[meta_list.index('?????????:') + 1] if '?????????:' in meta_list else ''

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
            # Some(times) are represented as 2018???4???
            published_at = published_at.replace("???", "-")
            published_at = published_at.replace("???", "-")
            published_at = published_at.replace("???", "-")
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

    # Parsing ???????????? (book introduction)
    book_intro_el = soup.select("#link-report")
    book_intro = ""
    if book_intro_el:
        if book_intro_el[0].select("span.short") and book_intro_el[0].select("span.all"):
            book_intro = book_intro_el[0].select(".intro")[1].contents
        else:
            book_intro = book_intro_el[0].select(".intro")[0].contents
        book_intro = list(map(lambda line: str(line), book_intro))
        book_intro = "".join(filter(lambda line: line != "\n" and line != " ", book_intro)).strip()

    # Parsing ???????????? (author introduction)
    author_title_el = soup.find("span", string="????????????")
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
    if len(toc_parts) > 0 and  '(??????)' in toc_parts[len(toc_parts) - 1]:
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

    return book_model({
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
    })


def _start(args):
    db_iterator = DB()
    db_updater = DB()
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
                books_data = list(tpool.map(lambda r: parse(r[0], r[1]), response_list))
                books_data = list(filter(lambda r: r != None, books_data))
                log.info(f"parsed {len(books_data)} books")

            try:
                db_updater.update_books_by_url(books_data)
                log.info(f"updated {len(books_data)} books")
            except Exception as err:
                db_updater.rollback()
                log.error("failed to update books")
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
