/*
Douban Crawler is a dead siple crawler for data scraping
Copyright (C) 2022 mogita <me@mogita.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
*/
CREATE TABLE IF NOT EXISTS books (
  id bigserial PRIMARY KEY,
  title text DEFAULT '',
  subtitle text DEFAULT '',
  author text DEFAULT '',
  author_url text DEFAULT '',
  author_intro text DEFAULT '',
  publisher text DEFAULT '',
  published_at timestamp without time zone DEFAULT NULL,
  original_title text DEFAULT '',
  translator text DEFAULT '',
  producer text DEFAULT '',
  series text DEFAULT '',
  price text DEFAULT '',
  isbn text DEFAULT '',
  pages int DEFAULT 0,
  bookbinding text DEFAULT '',
  book_intro text DEFAULT '',
  toc text DEFAULT '',
  rating real DEFAULT 0.0,
  rating_count int DEFAULT 0,
  cover_img_url text DEFAULT '',
  origin text DEFAULT '',
  origin_id text DEFAULT '',
  origin_url text UNIQUE DEFAULT '',
  crawled boolean DEFAULT False,
  created_at timestamp without time zone default (now() at time zone 'utc'),
  updated_at timestamp without time zone default (now() at time zone 'utc'),
  deleted_at timestamp without time zone default NULL
);

