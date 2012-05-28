UPDATE schema SET version=4;

ALTER TABLE organisations ADD COLUMN local_id BOOL;
ALTER TABLE departments ADD COLUMN local_id BOOL;
