ALTER TABLE IF EXISTS books ALTER COLUMN pages TYPE int USING (pages::integer);
ALTER TABLE IF EXISTS books ALTER COLUMN pages SET DEFAULT 0;