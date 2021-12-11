# Introduction

A dead simple crawler to get books information from Douban.

# Pre-requesites

- Python 3
- Install dependencies from `requirements.txt`
- (Optional) Install Anaconda to handle environment

# Usage

1. Run `get_tags` to fetch all the trending tags.

```bash
# This will generate a file tags.csv
python app.py get_tags
```

2. Run `crawl_books` to start crawling the books by the tags from the previous step.

```bash
python app.py crawl_books -i tags.csv
```

> Certainly, you can create the tags.csv without using the `get_tags` script. You might want to make sure the tags you specified can lead to any actual result of books.

# License

MIT © [mogita](https://github.com/mogita)
