#!/bin/sh

python app.py get_tags
python app.py crawl_books -i /data/tags.csv -o /data
