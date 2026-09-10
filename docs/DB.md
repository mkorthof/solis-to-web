# Database

create db manually:

````
sqlite3 solis.db
-- sqlite3> .read solis.sql

CREATE TABLE messages (
    datetime    TEXT PRIMARY KEY UNIQUE,
    payload     TEXT NOT NULL
);
```
