#!/bin/bash
set -e

echo "Loading first 1000 users..."
docker compose exec -T db psql -U hello_flask -d hello_flask_dev -c "
INSERT INTO users (username)
SELECT 'imported_user_' || gs
FROM generate_series(1, 1000) AS gs
ON CONFLICT (username) DO NOTHING;
"

echo "Loading credentials for imported users..."
docker compose exec -T db psql -U hello_flask -d hello_flask_dev -c "
INSERT INTO credentials (user_id, password_hash)
SELECT id, 'password'
FROM users
WHERE username LIKE 'imported_user_%'
ON CONFLICT (user_id) DO NOTHING;
"

echo "Loading first 1000 tweets..."
docker compose exec -T db psql -U hello_flask -d hello_flask_dev -c "
INSERT INTO tweets (user_id, body, created_at)
SELECT
    u.id,
    'Imported test tweet ' || gs || ' about big data postgres search',
    NOW() - (gs || ' seconds')::interval
FROM generate_series(1, 1000) AS gs
JOIN users u
  ON u.username = 'imported_user_' || gs;
"

echo "Done."
