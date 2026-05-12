![tests](https://github.com/daisydu1012/twitter-clone-final/actions/workflows/ci.yml/badge.svg)

# Twitter Clone Final Project

A database-backed Twitter clone built with Flask, PostgreSQL, Docker, Docker Compose, and Nginx.

## Features

- Create user accounts
- Login and logout
- Create messages
- Display the 20 most recent messages on the homepage
- Search messages using PostgreSQL full-text search
- Use a RUM index for fast search results

## Tech Stack

- Python
- Flask
- PostgreSQL
- PostgreSQL RUM extension
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
```
## Run the Application
### Development
```
docker compose up --build
```
### Production
```
docker compose -f docker-compose.prod.yml up --build
```

### After starting the containers, open:
```
http://localhost:8888
```

## Main Routes
/                 Home page
/login            Login
/logout           Logout
/create_account   Create account
/create_message   Create a new message
/search           Search tweets

## Database Schema

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

## Stop the Application
```
docker compose down
```

To remove volumes as well:
```
docker compose down -v
```
## Repository

https://github.com/daisydu1012/twitter-clone-final

## Notes
This project was developed as the final project for CSCI 143 Big Data at Claremont McKenna College.
