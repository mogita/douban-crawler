import csv
import time
import argparse
import logging
import requests
from os import path
from urllib.parse import quote, urlsplit
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np
from xpinyin import Pinyin
from bs4 import BeautifulSoup
from src.http import req, batch_req

log = logging.getLogger(__name__)
pinyin = Pinyin()

columns = [
    'title',
    'subtitle',
    'author',
    'publisher',
    'published_at',
    'price',
    'isbn',
    'pages',
    'bookbinding',
    'book_intro',
    'author_intro',
    'toc',
    'rating',
    'rating_count',
    'cover_img_url',
    'douban_book_id',
    'douban_url'
]

def _write_book_info(filepath, book_info_row):
    # Appending to the output file
    with open(filepath, "a", encoding="UTF-8") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL, quotechar = "'")
        writer.writerows(book_info_row)
        file.close()

def _write_headers(filepath):
    # Overwrite the output file
    with open(filepath, "w", encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerows([columns])
        file.close()


def _write_failure_info(filepath, failure_row):
    with open(filepath, "a", encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerows(failure_row)
        file.close()

def parse_book_info(source, url):
    soup = BeautifulSoup(source, 'html.parser')

    url_parts = urlsplit(url)
    path_parts = url_parts.path.split("/")
    douban_book_id = path_parts[2]

    book_meta = soup.select('#info')
    meta_list = list(book_meta[0].strings)
    meta_list = [i.strip() for i in meta_list if i.strip() != '']

    douban_url = url

    # Parsing a bunch of meta info
    title = soup.select("#wrapper > h1 > span")[0].contents[0]
    subtitle = meta_list[meta_list.index("副标题:") + 1] if "副标题:" in meta_list else ""

    author = ""
    if "作者:" in meta_list:
        author = meta_list[meta_list.index("作者:") + 1]
    elif soup.select("#info > span > a"):
        author = soup.select("#info > span > a")[0].contents[0]
    author = "".join(map(str.strip, author.split("\n")))

    publisher = meta_list[meta_list.index('出版社:') + 1] if '出版社:' in meta_list else ''
    published_at = meta_list[meta_list.index('出版年:') + 1] if '出版年:' in meta_list else ''
    price = meta_list[meta_list.index('定价:') + 1] if '定价:' in meta_list else ''
    isbn = meta_list[meta_list.index('ISBN:') + 1]  if 'ISBN:' in meta_list else ''
    pages = meta_list[meta_list.index('页数:') + 1] if '页数:' in meta_list else ''
    bookbinding = meta_list[meta_list.index('装帧:') + 1] if '装帧:' in meta_list else ''

    # Parsing 内容简介 (book introduction)
    book_intro_el = soup.select("#link-report")
    book_intro = ""
    if book_intro_el[0].select("span.short") and book_intro_el[0].select("span.all"):
        book_intro = book_intro_el[0].select(".intro")[1].contents
    else:
        book_intro = book_intro_el[0].select(".intro")[0].contents
    book_intro = list(map(lambda line: str(line), book_intro))
    book_intro = "".join(filter(lambda line: line != "\n" and line != " ", book_intro)).strip()

    # Parsing 作者简介 (author introduction)
    author_title_el = soup.find("span", string="作者简介")
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
    if len(toc_parts) > 0 and  '(收起)' in toc_parts[len(toc_parts) - 1]:
        toc_parts.pop()
    toc = "<br />".join(map(lambda line: line.replace("\u3000", " ").replace("\t", " ").strip(), toc_parts))

    # Parsing ratings
    rating_el = soup.select("#interest_sectl > div > div.rating_self.clearfix > strong")
    rating = rating_el[0].contents[0].strip() if rating_el else ""

    rating_count_el = soup.select("#interest_sectl > div > div.rating_self.clearfix > div > div.rating_sum > span > a > span")
    rating_count = rating_count_el[0].contents[0] if rating_count_el else ""

    # Parsing cover image
    cover_img_url = soup.select("#mainpic > a > img")[0].attrs["src"]

    return [title, subtitle, author, publisher, published_at, price, isbn, pages, bookbinding, book_intro, author_intro, toc, rating, rating_count, cover_img_url, douban_book_id, douban_url]


def _drain_tag(tag, args):
    page = 0
    page_size = 20
    base_url = f"https://book.douban.com/tag/{quote(tag)}"
    attempts = 0
    max_attempts = 3


    while(1):
        log.info(f"attempting listings page {page + 1}")

        url = f"{base_url}?start={page * page_size}&type=T"
        source, _ = req(url)
        soup = BeautifulSoup(source, "html.parser")
        book_list = soup.select("ul.subject-list > .subject-item")

        attempts += 1
        if book_list == None and attempts < max_attempts:
            continue
        elif book_list == None or len(book_list) <= 1:
            break

        log.info(f"{len(book_list)} books found")
        book_urls = list(map(lambda book_el: book_el.select('h2 > a')[0].get('href'), book_list))

        with ThreadPoolExecutor() as tpool:
            response_list = list(pool.map(req, book_urls))

        for book_source, book_url in response_list:
            try:
                book_row = parse_book_info(book_source, book_url)
                _write_book_info(path.join(args.output, f"{pinyin.get_pinyin(tag, tone_marks='numbers')}.csv"), [book_row])
                # Reset attempts for a valid piece of book information
                attempts = 0
            except Exception as err:
                log.error(err)
                _write_failure_info(path.join(args.output, f"{pinyin.get_pinyin(tag, tone_marks='numbers')}-failure.csv"), [[book_link]])
        page += 1


def _start(args):
    df = pd.read_csv(args.input)
    tags = df.name
    log.info(f"read {tags.size} tags")

    for _, tag in tags.iteritems():
        log.info(f"crawling tag {tag}...")
        _write_headers(path.join(args.output, f"{pinyin.get_pinyin(tag, tone_marks='numbers')}.csv"))
        _drain_tag(tag, args)


def main(raw_args=None):
    parser = argparse.ArgumentParser(
        description="Crawl book information from douban.com based on a CSV of tags. You can generate a CSV of tags with 'get_tags'."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to the input CSV file"
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to the output directory"
    )
    args = parser.parse_args(raw_args)

    _start(args)


if __name__ == "__main__":
    main()
