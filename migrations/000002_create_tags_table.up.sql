/*
Douban Crawler is a dead siple crawler for data scraping
Copyright (C) 2022 mogita <me@mogita.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
*/
CREATE TABLE IF NOT EXISTS tags (
  id bigserial PRIMARY KEY,
  name text UNIQUE NOT NULL,
  current_page bigint DEFAULT 0,
  created_at timestamp without time zone default (now() at time zone 'utc'),
  updated_at timestamp without time zone default (now() at time zone 'utc'),
  deleted_at timestamp without time zone default NULL
);
