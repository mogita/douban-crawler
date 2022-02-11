"""
Douban Crawler is a dead simple crawler for data scraping
Copyright (C) 2022 mogita <me@mogita.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
def book_model(attrs):
    data = (
        attrs['title'] if 'title' in attrs else "",
        attrs['subtitle'] if 'subtitle' in attrs else "",
        attrs['author'] if 'author' in attrs else "",
        attrs['author_url'] if 'author_url' in attrs else "",
        attrs['author_intro'] if 'author_intro' in attrs else "",
        attrs['publisher'] if 'publisher' in attrs else "",
        attrs['published_at'] if 'published_at' in attrs else None,
        attrs['original_title'] if 'original_title' in attrs else "",
        attrs['translator'] if 'translator' in attrs else "",
        attrs['producer'] if 'producer' in attrs else "",
        attrs['series'] if 'series' in attrs else "",
        attrs['price'] if 'price' in attrs else "",
        attrs['isbn'] if 'isbn' in attrs else "",
        attrs['pages'] if 'pages' in attrs else "0",
        attrs['bookbinding'] if 'bookbinding' in attrs else "",
        attrs['book_intro'] if 'book_intro' in attrs else "",
        attrs['toc'] if 'toc' in attrs else "",
        attrs['rating'] if 'rating' in attrs else 0,
        attrs['rating_count'] if 'rating_count' in attrs else 0,
        attrs['cover_img_url'] if 'cover_img_url' in attrs else "",
        attrs['origin'] if 'origin' in attrs else "",
        attrs['origin_id'] if 'origin_id' in attrs else "",
        attrs['origin_url'] if 'origin_url' in attrs else "",
        attrs['crawled'] if 'crawled' in attrs else False
    )
    if 'id' in attrs and attrs['id'] > 0:
        data = (attrs['id'],) + data
    return data

def tag_model(attrs):
    data = (
        attrs['name'] if 'name' in attrs else '',
        attrs['current_page_t'] if 'current_page_t' in attrs else 1,
        attrs['current_page_r'] if 'current_page_r' in attrs else 1,
        attrs['current_page_s'] if 'current_page_s' in attrs else 1,
        attrs['exhausted_t'] if 'exhausted_t' in attrs else False,
        attrs['exhausted_r'] if 'exhausted_r' in attrs else False,
        attrs['exhausted_s'] if 'exhausted_s' in attrs else False
    )
    if 'id' in attrs and attrs['id'] > 0:
        data = (attrs['id'],) + data
    return data


def doulist_model(attrs):
    data = (
        attrs['list_id'] if 'list_id' in attrs else '',
        attrs['current_page'] if 'current_page' in attrs else 0,
        attrs['exhausted'] if 'exhausted' in attrs else False
    )
    if 'id' in attrs and attrs['id'] > 0:
        data = (attrs['id'],) + data
    return data
