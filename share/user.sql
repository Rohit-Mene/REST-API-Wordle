-- $ sqlite3 ./var/project1.db < ./share/validword.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS USERDATA;
CREATE TABLE USERDATA(
user_name text not null,
user_pass text not null,
user_id INTEGER PRIMARY KEY AUTOINCREMENT,
UNIQUE(user_name)
);
CREATE INDEX USERDATA_idx_861e4408 ON USERDATA(user_name, user_pass);
COMMIT;

INSERT INTO USERDATA(user_name, user_pass) VALUES('client','admin');