"""
Douban Crawler is a dead siple crawler for data scraping
Copyright (C) 2022 mogita <me@mogita.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
import time
import logging
import argparse
from bs4 import BeautifulSoup
import numpy as np
from src.http import req
from src.model import tag_model
from src.db import DB

log = logging.getLogger(__name__)

def main(raw_args=None):
    parser = argparse.ArgumentParser(
        description="Fetch the tags from Douban books and output a CSV file containing these tags."
    )
    args = parser.parse_args(raw_args)

    urls = [
        "https://book.douban.com/tag/?view=type",
        "https://book.douban.com/tag/?view=cloud"
    ]

    for url in urls:
        source, _ = req(url)
        soup = BeautifulSoup(source, "html.parser")
        tags = list(map(lambda r: [r.select("a")[0].contents[0]], soup.findAll("td")))

        tag_models = list(map(lambda r: tag_model({'name': r[0]}), tags))
        log.debug(tag_models)

        # save tags to db
        try:
            if tag_models != None:
                log.info(f"saving {len(tag_models)} tags to database...")
                db = DB()
                db.insert_tags(tag_models)
        except Exception as err:
            log.error("failed to save the tags to database")
            log.error(err)

        time.sleep(np.random.rand()*5)


if __name__ == "__main__":
    main()
