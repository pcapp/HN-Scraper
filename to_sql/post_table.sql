CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    deleted BOOLEAN NOT NULL DEFAULT false,
    by TEXT NOT NULL,
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    text TEXT,
    dead BOOLEAN NOT NULL DEFAULT false,
    url VARCHAR(2048),
    title TEXT,
    CONSTRAINT fk_user FOREIGN KEY (by) REFERENCES users(id)
);

