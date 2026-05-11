CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS rum;

DROP TABLE IF EXISTS tweets CASCADE;
DROP TABLE IF EXISTS credentials CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE credentials (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    password_hash TEXT NOT NULL
);

CREATE TABLE tweets (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_username
    ON users(username);

CREATE INDEX idx_tweets_created_at
    ON tweets(created_at DESC);

CREATE INDEX idx_tweets_user_id
    ON tweets(user_id);

CREATE INDEX idx_tweets_fts
    ON tweets
    USING rum(to_tsvector('english', body));
