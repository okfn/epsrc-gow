UPDATE schema SET version=3;

ALTER TABLE departments DROP COLUMN local_id BOOL;
ALTER TABLE organisations DROP COLUMN local_id BOOL;
