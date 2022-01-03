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

def _get_book_links_from_tag(tag_data):
    tag = tag_data['name']
    page = tag_data['current_page']
    page_size = 20
    base_url = f"https://book.douban.com/tag/{quote(tag)}"
    attempts = 0
    max_attempts = 3

    while(1):
        log.info(f"attempting on page {page} for tag {tag}")

        time.sleep(np.random.rand()*5)

        url = f"{base_url}?start={page * page_size}&type=T"
        source = None
        try:
            source, _ = req(url)
        except Exception as err:
            log.error(err)

        attempts += 1
        if source == None:
            if attempts< max_attempts:
                log.warn(f"failed to fetch page {page} for tag {tag}, will retry")
                continue
            else:
                log.warn(f"failed to fetch page {page} for tag {tag}, exhausted and abort")
                break

        soup = BeautifulSoup(source, "html.parser")
        book_list = soup.select("ul.subject-list > .subject-item")

        if book_list == None and attempts < max_attempts:
            log.warn(f"no books on page {page}, will retry")
            continue
        elif book_list == None or len(book_list) <= 1:
            log.warn(f"no books on page {page}, exhausted and abort")
            break

        book_urls = list(map(lambda book_el: book_el.select('h2 > a')[0].get('href'), book_list))
        book_data = list(map(lambda link: book_model({ 'origin_url': link }), book_urls))
        try:
            db.insert_books(book_data)
            log.info(f"saved {len(book_data)} books for tag {tag} on page {page}")
        except Exception as err:
            db.rollback()
            log.error(f"failed to save book links for tag {tag} on page {page}")
            log.error(err)

        page += 1
        try:
            db.update_tags([tag_model({'id': tag_data['id'], 'name': tag, 'current_page': page})])
        except Exception as err:
            db.rollback()
            log.error(f"failed to update tag {tag}")
            log.error(err)


def _start():
    tags = db.get_tags()
    log.info(f"read {len(tags)} tags")

    for tag in tags:
        log.info(f"getting links from tag {tag['name']}...")
        _get_book_links_from_tag(tag)


def main(raw_args=None):
    parser = argparse.ArgumentParser(
        description="Crawl book links from douban.com from the given tags. You can generate the tags with 'get_tags' script."
    )
    args = parser.parse_args(raw_args)

    _start()


if __name__ == "__main__":
    main()
