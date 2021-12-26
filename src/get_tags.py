import logging
import argparse
from bs4 import BeautifulSoup
import numpy as np
from os import environ as env
from dotenv import load_dotenv
from src.http import req, req_with_proxy
from src.proxy_pool import get_count
from src.model import tag_model
from src.db import DB

log = logging.getLogger(__name__)

load_dotenv()
w_proxy = False if env.get("WITHOUT_PROXY") == "yes" else True
log.info(env.get("WITHOUT_PROXY"))

def main(raw_args=None):
    parser = argparse.ArgumentParser(
        description="Fetch the tags from Douban books and output a CSV file containing these tags."
    )
    args = parser.parse_args(raw_args)

    url = "https://book.douban.com/tag/"

    if w_proxy:
        if get_count() == 0:
            log.error("proxy pool is empty, mission aborted")
            return
        source, _ = req_with_proxy(url)
    else:
        source, _ = req(url)

    soup = BeautifulSoup(source, "html.parser")
    tags = list(map(lambda r: [r.select("a")[0].contents[0]], soup.findAll("td")))

    tag_models = list(map(lambda r: tag_model({'name': r[0], 'current_page': 0}), tags))
    log.info(tag_models)

    # save tags to db



if __name__ == "__main__":
    main()
