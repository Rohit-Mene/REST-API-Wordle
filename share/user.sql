-- $ sqlite3 ./var/project1.db < ./share/validword.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS USERDATA;
CREATE TABLE USERDATA(
user_name text not null,
user_pass text not null,
user_id INTEGER PRIMARY KEY AUTOINCREMENT
);

COMMIT;
