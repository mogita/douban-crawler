import logging
import argparse
import csv
from bs4 import BeautifulSoup
import numpy as np
from os import path
from src.http import req
from src.proxy_pool import get_count

log = logging.getLogger(__name__)

def main(raw_args=None):
    parser = argparse.ArgumentParser(
        description="Fetch the tags from Douban books and output a CSV file containing these tags."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to the output directory"
    )
    args = parser.parse_args(raw_args)

    if get_count() == 0:
        log.error("proxy pool is empty, mission aborted")
        return

    url = "https://book.douban.com/tag/"
    source, _ = req(url)
    soup = BeautifulSoup(source, "html.parser")
    tags = list(map(lambda r: [r.select("a")[0].contents[0]], soup.findAll("td")))
    log.info(tags)

    tags.insert(0, ['name'])

    with open(path.join(args.output, "tags.csv"), "w", encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerows(tags)
        log.info(f"saved {len(tags) - 1} entries to {args.output}/tags.csv")


if __name__ == "__main__":
    main()
