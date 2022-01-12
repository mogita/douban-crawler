ALTER TABLE IF EXISTS tags RENAME COLUMN exhausted TO exhausted_t;
ALTER TABLE IF EXISTS tags ADD COLUMN exhausted_r boolean DEFAULT false;
ALTER TABLE IF EXISTS tags ADD COLUMN exhausted_s boolean DEFAULT false;
