CREATE TABLE stories (
    id INTEGER PRIMARY KEY,
    by TEXT NOT NULL,
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    text TEXT,
    dead BOOLEAN NOT NULL DEFAULT false,
    url VARCHAR(2048),
    title TEXT,
    score INTEGER NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY (by) REFERENCES users(id)
);

