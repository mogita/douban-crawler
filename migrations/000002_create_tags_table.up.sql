CREATE TABLE IF NOT EXISTS tags (
  id bigserial PRIMARY KEY,
  tag text UNIQUE NOT NULL,
  created_at timestamp without time zone default (now() at time zone 'utc'),
  updated_at timestamp without time zone default (now() at time zone 'utc'),
  deleted_at timestamp without time zone default NULL
);
