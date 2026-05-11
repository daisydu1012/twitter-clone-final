![tests](https://github.com/daisydu1012/flask-on-docker/actions/workflows/tests.yml/badge.svg)
# Flask on Docker

A production-ready Flask application containerized with Docker and served with Gunicorn and Nginx.  
The app supports PostgreSQL, static files, and user-uploaded media.

## Overview

This project demonstrates how to deploy a full Flask stack using Docker Compose.  
It includes a Flask backend, a Postgres database, and an Nginx reverse proxy.  
Users can upload an image through the web interface and access it through a public URL.

## Demo

![Demo](assets/demo.gif)

The demo shows:

- starting the containers
- uploading an image
- accessing the uploaded file from the browser

---

## Tech Stack

- Flask
- PostgreSQL
- Gunicorn
- Nginx
- Docker & Docker Compose

---

## Project Structure

```
.
├── services/
│ ├── web/
│ └── nginx/
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

---

## Build & Run (Development)

```bash
docker compose up --build

App will be available at:

http://localhost:5001
Build & Run (Production)
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py create_db

App will be available at:

http://localhost:8888
Upload a File

Go to:

http://localhost:8888/upload

After uploading:

http://localhost:8888/media/<filename>
Stop Containers
docker compose down -v
Notes

.env.prod.db is excluded from version control for security

Volumes are used for persistent database, static files, and media

Nginx serves static and media files directly in production
