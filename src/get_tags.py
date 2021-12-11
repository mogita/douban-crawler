import logging
import csv
import requests
from bs4 import BeautifulSoup
import numpy as np
from src.ua import get_a_random_ua

log = logging.getLogger(__name__)

def main():
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

    with open("tags.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerows(tags)
        log.info(f"saved {len(tags) - 1} entries to tags.csv")



if __name__ == "__main__":
    main()
