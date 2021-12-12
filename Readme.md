# Introduction

A dead simple crawler to get books information from Douban.

# Pre-requesites

- Python 3
- Install dependencies from `requirements.txt`
- (Optional) Install Anaconda to handle environment

# Usage

## On Local Machine

1. Run `get_tags` to fetch all the trending tags.

```bash
# This will generate a file tags.csv
python app.py get_tags -o /your-output-dir
```

2. Run `crawl_books` to start crawling the books by the tags from the previous step.

```bash
python app.py crawl_books -i /some-where/tags.csv -o /your-output-dir
```

> Certainly, you can create the tags.csv without using the `get_tags` script. You might want to make sure the tags you specified can lead to any actual result of books.

## Docker Compose

You'll need to install [`Docker`](https://docs.docker.com/engine/install/) and the [`docker-compose`](https://docs.docker.com/compose/install/) command before proceeding.

```bash
docker-compose build --no-cache && docker-compose up -d --force-recreate
```

You can omit `--force-recreate` if you want to keep the container when the configuration or the image hasn't changed.

# License

MIT © [mogita](https://github.com/mogita)
