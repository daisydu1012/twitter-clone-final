![tests](https://github.com/daisydu1012/twitter-clone-final/actions/workflows/ci.yml/badge.svg)

# Twitter Clone Final Project

A database-backed Twitter clone built with Flask, PostgreSQL, Docker, Docker Compose, and Nginx.

## Features

- Create user accounts
- Login and logout
- Create tweets
- Display the 20 most recent tweets on the homepage
- Pagination for older tweets
- Full-text search using PostgreSQL
- Search result highlighting with `ts_headline`
- Search result ranking with `ts_rank_cd`
- Spelling suggestions for misspelled queries using `pg_trgm` (extra credit)
- RUM index for fast search performance

## Tech Stack

- Python 3
- Flask
- PostgreSQL
- PostgreSQL extensions:
  - `rum`
  - `pg_trgm`
- Docker
- Docker Compose
- Nginx
- GitHub Actions CI

## Project Structure

```
twitter-clone-final/
├── .github/workflows/ci.yml
├── assets/
├── services/
│   ├── nginx/
│   ├── postgres/
│   │   ├── Dockerfile
│   │   ├── schema.sql
│   │   └── scripts/
│   │       ├── load_test_data.sh
│   │       └── load_test_data_small.sh
│   └── web/
│       ├── Dockerfile
│       ├── Dockerfile.prod
│       ├── manage.py
│       ├── project/
│       │   ├── __init__.py
│       │   └── config.py
│       └── requirements.txt
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.dev
└── README.md
```


## Database Schema

The database contains three core tables:

### users
Stores user accounts.

| Column | Type | Description |
|------|------|------|
| id | SERIAL PRIMARY KEY | User ID |
| username | TEXT UNIQUE NOT NULL | Username |

### credentials
Stores password hashes.

| Column | Type | Description |
|------|------|------|
| user_id | INTEGER PRIMARY KEY | References users(id) |
| password_hash | TEXT NOT NULL | Hashed password |

### tweets
Stores messages posted by users.

| Column | Type | Description |
|------|------|------|
| id | BIGSERIAL PRIMARY KEY | Tweet ID |
| user_id | INTEGER NOT NULL | References users(id) |
| body | TEXT NOT NULL | Tweet content |
| created_at | TIMESTAMP NOT NULL | Creation timestamp |
| tsv | TSVECTOR | Full-text search vector |


## Indexes

- Primary keys on all tables
- Unique index on `users.username`
- RUM index on `tweets.tsv`
- Trigram index for spelling suggestions


## Loading Test Data

The project includes a script that loads over one million rows into the database.

```
./services/postgres/scripts/load_test_data.sh
```
This script inserts:

1,000,000 users
1,000,000 credentials
1,000,000 tweets

A smaller debugging script is also included:
```
./services/postgres/scripts/load_test_data_small.sh
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

After starting the containers, open:

http://localhost:8888

## Main Routes

- `/` — Home page
- `/login` — Login
- `/logout` — Logout
- `/create_account` — Create account
- `/create_message` — Create a new message
- `/search` — Search tweets

## Search Features

The `/search` route supports:

-PostgreSQL full-text search
-Relevance ranking
-Highlighted matching terms
-Pagination
-Typo suggestions

Example:

-Searching for data returns tweets containing “data”.
-Searching for datta suggests data.


## Stop the Application

```
docker compose down
```

To remove volumes as well:
```
docker compose down -v
```

## Example Workflow
1. Create an account.
2. Log in.
3. Create a tweet.
4. View tweets on the homepage.
5. Search tweets by keyword.
6. Receive spelling suggestions for misspelled searches.
7. Log out.

## Performance

The project uses:

RUM indexes for efficient ranked full-text search.
pg_trgm for fast similarity matching.
Over one million rows of test data to demonstrate scalability.

## Repository

https://github.com/daisydu1012/twitter-clone-final

## Notes

This project was developed as the final project for CSCI 143 Big Data at Claremont McKenna College.
