CREATE TABLE IF NOT EXISTS tags (
  id bigserial PRIMARY KEY,
  name text UNIQUE NOT NULL,
  current_page bigint DEFAULT 0,
  created_at timestamp without time zone default (now() at time zone 'utc'),
  updated_at timestamp without time zone default (now() at time zone 'utc'),
  deleted_at timestamp without time zone default NULL
);
