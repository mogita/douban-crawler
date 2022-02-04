# Introduction

A dead simple crawler for data scraping from Douban.

**Heads-up: this project is under heavy development and things shall change or even break from time to time till further stated. You can track the progress on this [Trello board](https://trello.com/b/ff2YcyvR/douban-crawler).**

# Usage

This crawler depends on the [proxy_pool](https://github.com/jhao104/proxy_pool) for making concurrent anonymous requests. The crawler has built-in support that makes it pretty easy to customize and run your own instance of the proxy pool service.

## Prerequisites

- [Docker](https://docs.docker.com/engine/install/)
- [docker-compose](https://docs.docker.com/compose/install/)

## Steps

### Without the Proxy Pool

1. Create a `.env` file under the project root and add the following line:

```bash
WITHOUT_PROXY=yes
```

2. Build and start

```bash
# You can add `--no-cache` to always build a clean image
docker-compose build

# You can add `--force-recreate` if you want to drop the container even when 
# the configuration or the image hasn't changed.
docker-compose up -d
```

> Not using proxies might lead to 403 error responses from the source site.

### With the Proxy Pool

1. Free IPs just don't work most of the time. It's highly recommended that you choose a payed proxy provider and tweak the code under `proxy_pool` directory to override the functionality and suit your needs. Take Zhima (芝麻) HTTP Proxy for example, create a `.env` file and put the API endpoint into it:

```env
ZHIMA_PROXY_URL="https://..."
```

2. Build and start

```bash
# Start the proxy_pool containers first, and you might want to wait for a while
# to make sure there's IP available in the pool by looking at the logs of 
# container "douban-crawler-proxy-pool". With available IPs you're good to go 
# to the next command.
docker-compose -f docker-compose.proxy.yml up -d

# You can add `--no-cache` to always build a clean image
docker-compose build

# You can add `--force-recreate` if you want to drop the container even when 
# the configuration or the image hasn't changed.
docker-compose up -d
```

# Development

## Prerequisites

- Python 3 with `pip`
- PostgreSQL
- Redis
- [proxy_pool](https://github.com/jhao104/proxy_pool)

> It might be a bit more convenient to use Virtualenv or Anaconda to handle the environment. But this differs from case to case so please know what you're dealing with before going ahead.

## Steps

1. This project depends on `proxy_pool` for making anonymous requests. You should either setup your own instance or if yor're super lazy just try your luck with the free server setup by the [proxy_pool](https://github.com/jhao104/proxy_pool) project. You should be warned about the super low usability of the free IPs. To customize the fetching method for different providers, tweak the code under `proxy_pool/fetcher` directory. Please refer to the docs of `proxy_pool` to learn more.

Edit `.env` file to set the proper environment variables:

```bash
# Adding the following line will make the scripts show verbose logs
DEBUG=yes

# As I'm using Zhima HTTP Proxy I'll put the API here so proxy_pool/fetcher knows 
# where to get new IPs to refresh the pool. 
ZHIMA_PROXY_URL="https://..."

# Put the host name and port (if needed) here for the "proxy_pool" instance so this
# crawler knows where the pool is.
PROXY_POOL_HOST="https://localhost:5010"

# Anyway if you don't need the proxy pool at all, e.g. you want the script to 
# make request directly from your network, you can add the following line and
# go to step 2
WITHOUT_PROXY=yes
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Migrate database schemas

First you should install `golang-migrate/migrate` tool to enable the `migrate` command. Follow the installation guides here: [`migrate CLI`](https://github.com/golang-migrate/migrate/tree/master/cmd/migrate).

Then make the migration to your database (change the `user`, `pass` and/or hostname and port accordingly):

```bash
migrate -database "postgres://user:pass@localhost:5432/crawler?sslmode=disable" -path migrations up
```

4. Run the scripts in the following sequence:

```bash
# First, get as more as possible tags
python app.py get_tags

# Second, iterate through tags and fetch the links to the books
python app.py get_book_links_by_tag

# Optionally, get links from doulists (list IDs need to be manually added to the database beforehand)
python app.py get_book_links_by_doulist

# Lastly start to crawl books from the links
python app.py crawl_books
```

# License

AGPLv3 © [mogita](https://gitlab.com/mogita)
