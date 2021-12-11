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

> Certainly, you can write a tags.csv without the `get_tags` step. You'll have to make sure the tags you specified can lead to any actual result of books.

# License

MIT © [mogita](https://github.com/mogita)
