"""
Douban Crawler is a dead siple crawler for data scraping
Copyright (C) 2022 mogita <me@mogita.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
import argparse
import time
import logging
from urllib.parse import quote
import numpy as np
from bs4 import BeautifulSoup
from src.db import DB
from src.http import req
from src.model import doulist_model, book_model

log = logging.getLogger(__name__)

db = DB()


def _get_book_links_from_doulist(doulist_data):
    list_id = doulist_data['list_id']
    page = doulist_data['current_page']
    page_size = 25
    base_url = f"https://www.douban.com/doulist/{list_id}/"
    attempts = 0
    max_attempts = 3

    while(1):
        log.info(f"attempting on page {page} for doulist {list_id}")

        time.sleep(np.random.rand()*5)

        url = f"{base_url}?start={page * page_size}"
        source = None
        try:
            source, _ = req(url)
        except Exception as err:
            log.error(err)

        attempts += 1
        if source == None:
            if attempts< max_attempts:
                log.warn(f"failed to fetch page {page} for doulist {list_id}, will retry")
                continue
            else:
                log.warn(f"failed to fetch page {page} for doulist {list_id}, exhausted and abort")
                break

        soup = BeautifulSoup(source, "html.parser")
        book_list = soup.select(".article > .doulist-item")

        if book_list == None and attempts < max_attempts:
            log.warn(f"no books on page {page}, will retry")
            continue
        elif book_list == None or len(book_list) <= 1:
            log.warn(f"no books on page {page}, exhausted and abort")
            try:
                doulist_data[f'current_page'] = page
                doulist_data[f'exhausted'] = True
                db.update_doulists([doulist_model(doulist_data)])
            except Exception as err:
                db.rollback()
                log.error(f"failed to update doulist {list_id} to exhausted")
                log.error(err)
            break

        book_urls = list(map(lambda book_el: book_el.select('div.title > a')[0].get('href'), book_list))
        # Since doulists are user created, here's a filter to make sure only books are saved at this time
        book_urls = list(filter(lambda url: url.find("book.douban.com") >= 0, book_urls))
        book_data = list(map(lambda link: book_model({ 'origin_url': link }), book_urls))
        try:
            db.insert_books(book_data)
            log.info(f"saved {len(book_data)} books for doulist {list_id} on page {page}")
        except Exception as err:
            db.rollback()
            log.error(f"failed to save book links for {list_id} on page {page}")
            log.error(err)

        page += 1
        try:
            doulist_data[f'current_page'] = page
            db.update_doulists([doulist_model(doulist_data)])
        except Exception as err:
            db.rollback()
            log.error(f"failed to update doulist {list_id}")
            log.error(err)


def _start():
    doulists = db.get_doulists()
    log.info(f"read {len(doulists)} doulists")

    for doulist in doulists:
        log.info(f"getting links from doulist {doulist['list_id']}...")
        _get_book_links_from_doulist(doulist)

    log.info("all doulists exhausted")


def main(raw_args=None):
    parser = argparse.ArgumentParser(
        description="Crawl book links from douban.com from the given doulists. Currently doulists need to be manually added to the database before running this script."
    )
    args = parser.parse_args(raw_args)

    _start()


if __name__ == "__main__":
    main()
