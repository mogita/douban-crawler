ALTER TABLE IF EXISTS tags RENAME COLUMN current_page_t TO current_page;
ALTER TABLE IF EXISTS tags DROP COLUMN current_page_r;
ALTER TABLE IF EXISTS tags DROP COLUMN current_page_s;
