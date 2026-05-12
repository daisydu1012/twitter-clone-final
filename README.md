![tests](https://github.com/daisydu1012/twitter-clone-final/actions/workflows/ci.yml/badge.svg)

# Twitter Clone Final Project

A database-backed Twitter clone built with Flask, PostgreSQL, Docker, Docker Compose, and Nginx.

## Features

- Create user accounts
- Login and logout
- Create messages
- Display recent messages on the homepage
- Search messages using PostgreSQL full-text search
- Use a RUM index for fast search

## Tech Stack

- Python
- Flask
- PostgreSQL
- PostgreSQL RUM Extension
- SQLAlchemy
- Docker
- Docker Compose
- Nginx
- GitHub Actions

## Project Structure

```text
.
├── services/
│   ├── web/
│   ├── postgres/
│   └── nginx/
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md

##Run the Application
```
docker compose up --build
```

Then open: 
http://localhost:8888

##Main Routes

/                 Home page
/login            Login
/logout           Logout
/create_account   Create account
/create_message   Create a new message
/search           Search tweets


##Database Schema
The database contains three tables:

users
credentials
tweets

The tweets table uses a RUM full-text search index:
```
CREATE INDEX idx_tweets_fts
ON tweets
USING rum(to_tsvector('english', body));

```

##Stop the Application
```
docker compose down
```

To also remove volumes: 
```
docker compose down -v
```






