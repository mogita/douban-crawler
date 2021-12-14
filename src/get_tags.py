import logging
import argparse
import csv
import requests
from bs4 import BeautifulSoup
import numpy as np
from src.ua import get_a_random_ua

log = logging.getLogger(__name__)

def main(raw_args=None):
    parser = argparse.ArgumentParser(
        description="Fetch the tags from Douban books and output a CSV file containing these tags."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to the output directory"
    )
    args = parser.parse_args(raw_args)

    url = "https://book.douban.com/tag/"
    try:
        content = requests.get(url, headers={'User-Agent': get_a_random_ua()})
        source = content.text
    except e:
        log.error(e)
        exit(1)

    soup = BeautifulSoup(source, "html.parser")
    tags = list(map(lambda r: [r.select("a")[0].contents[0]], soup.findAll("td")))
    log.info(tags)

    tags.insert(0, ['name'])

    with open(f"{args.output}/tags.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerows(tags)
        log.info(f"saved {len(tags) - 1} entries to {args.output}/tags.csv")



if __name__ == "__main__":
    main()
