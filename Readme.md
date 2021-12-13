# Introduction

A dead simple crawler for data scraping from Douban.

**Heads-up: this project is under heavy development and things shall change or even break from time to time till further stated. You can track the progress on this [Trello board](https://trello.com/b/ff2YcyvR/douban-crawler).**

# Usage

## On Local Machine

### Prerequisites

- Python 3 with `pip`
- Redis
- [proxy_pool](https://github.com/jhao104/proxy_pool)

> It's recommended to use Anaconda to handle the environment.

### Steps

1. Install dependencies.

```bash
pip install -r requirements.txt
```

2. Run `get_tags` to fetch all the trending tags.

```bash
# This will generate a file tags.csv
python app.py get_tags -o /your-output-dir
```

3. Run `crawl_books` to start crawling the books by the tags from the previous step.

```bash
python app.py crawl_books -i /some-where/tags.csv -o /your-output-dir
```

> Certainly, you can create the tags.csv without using the `get_tags` script. You might want to make sure the tags you specified can lead to any actual result of books.

## Docker Compose

### Prerequisites

- [Docker](https://docs.docker.com/engine/install/)
- [docker-compose](https://docs.docker.com/compose/install/)

```bash
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

You can omit `--force-recreate` if you want to keep the container when the configuration or the image hasn't changed.

# License

MIT © [mogita](https://github.com/mogita)
