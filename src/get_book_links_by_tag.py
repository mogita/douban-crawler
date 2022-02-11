"""
Douban Crawler is a dead simple crawler for data scraping
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
from src.model import tag_model, book_model

log = logging.getLogger(__name__)

db = DB()


def _get_book_links_from_tag_by_default(tag_data):
    _get_book_links_from_tag(tag_data, "t")


def _get_book_links_from_tag_by_publish_date(tag_data):
    _get_book_links_from_tag(tag_data, "r")


def _get_book_links_from_tag_by_rate(tag_data):
    _get_book_links_from_tag(tag_data, "s")


def _get_book_links_from_tag(tag_data, type_value):
    tag = tag_data['name']
    page = tag_data[f'current_page_{type_value}']
    page_size = 20
    base_url = f"https://book.douban.com/tag/{quote(tag)}"
    attempts = 0
    max_attempts = 3

    while(1):
        log.info(f"attempting on page {page} for tag {tag}")

        time.sleep(np.random.rand()*5)

        url = f"{base_url}?start={page * page_size}&type={type_value.upper()}"
        source = None
        try:
            source, _ = req(url)
        except Exception as err:
            log.error(err)

        attempts += 1
        if source == None:
            if attempts< max_attempts:
                log.warn(f"failed to fetch page {page} for tag {tag} {type_value.upper()}, will retry")
                continue
            else:
                log.warn(f"failed to fetch page {page} for tag {tag} {type_value.upper()}, exhausted and abort")
                break

        soup = BeautifulSoup(source, "html.parser")
        book_list = soup.select("ul.subject-list > .subject-item")

        if book_list == None and attempts < max_attempts:
            log.warn(f"no books on page {page}, will retry")
            continue
        elif book_list == None or len(book_list) <= 1:
            log.warn(f"no books on page {page}, exhausted and abort")
            try:
                tag_data[f'current_page_{type_value}'] = page
                tag_data[f'exhausted_{type_value}'] = True
                db.update_tags([tag_model(tag_data)])
            except Exception as err:
                db.rollback()
                log.error(f"failed to update tag {tag} {type_value.upper()} to exhausted")
                log.error(err)
            break

        book_urls = list(map(lambda book_el: book_el.select('h2 > a')[0].get('href'), book_list))
        book_data = list(map(lambda link: book_model({ 'origin_url': link }), book_urls))
        try:
            db.insert_books(book_data)
            log.info(f"saved {len(book_data)} books for tag {tag} {type_value.upper()} on page {page}")
        except Exception as err:
            db.rollback()
            log.error(f"failed to save book links for tag {tag} {type_value.upper()} on page {page}")
            log.error(err)

        page += 1
        try:
            tag_data[f'current_page_{type_value}'] = page
            db.update_tags([tag_model(tag_data)])
        except Exception as err:
            db.rollback()
            log.error(f"failed to update tag {tag} {type_value.upper()}")
            log.error(err)


def _start():
    tags = db.get_tags()
    log.info(f"read {len(tags)} tags")

    for tag in tags:
        log.info(f"getting links from tag {tag['name']} by default sorting...")
        _get_book_links_from_tag_by_default(tag)

        log.info(f"getting links from tag {tag['name']} by publish date sorting...")
        _get_book_links_from_tag_by_publish_date(tag)

        log.info(f"getting links from tag {tag['name']} by rate sorting...")
        _get_book_links_from_tag_by_rate(tag)

    log.info("all tags exhausted")


def main(raw_args=None):
    parser = argparse.ArgumentParser(
        description="Crawl book links from douban.com from the given tags. You can generate the tags with 'get_tags' script."
    )
    args = parser.parse_args(raw_args)

    _start()


if __name__ == "__main__":
    main()
