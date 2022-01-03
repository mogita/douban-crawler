#!/bin/sh

echo "getting tags..."
python app.py get_tags

echo "getting book links..."
python app.py get_book_links

echo "crawling books..."
python app.py crawl_books
