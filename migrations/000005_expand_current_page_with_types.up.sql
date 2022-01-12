ALTER TABLE IF EXISTS tags RENAME COLUMN current_page TO current_page_t;
ALTER TABLE IF EXISTS tags ADD COLUMN current_page_r bigint DEFAULT 0;
ALTER TABLE IF EXISTS tags ADD COLUMN current_page_s bigint DEFAULT 0;
