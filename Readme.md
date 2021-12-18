# Introduction

A dead simple crawler for data scraping from Douban.

**Heads-up: this project is under heavy development and things shall change or even break from time to time till further stated. You can track the progress on this [Trello board](https://trello.com/b/ff2YcyvR/douban-crawler).**

# Usage

This crawler depends on the [proxy_pool](https://github.com/jhao104/proxy_pool) for making concurrent anonymous requests. The crawler has built-in support that makes it pretty easy to customize and run your own instance of the proxy pool service.

## Prerequisites

- [Docker](https://docs.docker.com/engine/install/)
- [docker-compose](https://docs.docker.com/compose/install/)

## Steps

1. Free IPs just don't work most of the time. It's highly recommended that you choose a payed proxy provider and tweak the code under `proxy_pool` directory to override the functionality and suit your needs. Take Zhima (芝麻) HTTP Proxy for example, create a `.env` file and put the API endpoint into it:

```env
ZHIMA_PROXY_URL="https://..."
```

2. Build and start

```bash
# Start the proxy_pool containers first, and you might want to wait for a while to make sure there's IP available in the pool by looking at the logs of container "douban-crawler-proxy-pool". With available IPs you're good to go to the next command.
docker-compose -f docker-compose.proxy.yml up -d

# You can add `--no-cache` to always build a clean image
docker-compose build

# You can add `--force-recreate` if you want to drop the container even when the configuration or the image hasn't changed.
docker-compose up -d
```

# Development

## Prerequisites

- Python 3 with `pip`
- Redis
- [proxy_pool](https://github.com/jhao104/proxy_pool)

> It's recommended to use Virtualenv or Anaconda to handle the environment.

## Steps

1. This project depends on `proxy_pool` for making anonymous requests. You should either setup your own instance or if yor're super lazy just try your luck with the free server setup by the [proxy_pool](https://github.com/jhao104/proxy_pool) project. You should be warned about the super low usability of the free IPs. To customize providers fetching method, tweak the code under `proxy_pool/fetcher` directory.

Edit `.env` file to set the proper environment variables:

```bash
# As I'm using Zhima HTTP Proxy I'll put the API here so proxy_pool/fetcher can request the provider and get new IPs. 
ZHIMA_PROXY_URL="https://..."

# Put the host and port here for the "proxy_pool" instance, whether it's running locally, on your VPS or using the public one.
PROXY_POOL_HOST="https://localhost:5010"
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Run `get_tags` to fetch all the trending tags.

```bash
# This will generate a file tags.csv
PROXY_POOL_HOST=https://<host-of-step-1>... python app.py get_tags -o /your-output-dir
```

4. Run `crawl_books` to start crawling the books by the tags from the previous step.

```bash
PROXY_POOL_HOST=https://<host-of-step-1>... python app.py crawl_books -i /some-where/tags.csv -o /your-output-dir
```

> Certainly, you can create the tags.csv without using the `get_tags` script. You may want to make sure the tags you specified can lead to any actual result of books.

# License

MIT © [mogita](https://github.com/mogita)
