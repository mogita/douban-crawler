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

    url = "https://book.douban.com/tag/"

    source, _ = req(url)
    soup = BeautifulSoup(source, "html.parser")
    tags = list(map(lambda r: [r.select("a")[0].contents[0]], soup.findAll("td")))

    tag_models = list(map(lambda r: tag_model({'name': r[0]}), tags))
    log.debug(tag_models)

    # save tags to db
    try:
        db = DB()
        db.insert_tags(tag_models)
        log.info(f"saved {len(tag_models)} tags to db")
    except Exception as err:
        log.error("failed to save the tags to db")
        log.error(err)



if __name__ == "__main__":
    main()
