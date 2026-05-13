#!/bin/bash
set -e

BASE_URL="http://localhost:8888"

echo "1. Testing homepage..."
curl -s "$BASE_URL/" | grep -q "Twitter Clone"
echo "Homepage OK"

echo "2. Testing login page..."
curl -s "$BASE_URL/login" | grep -q "Login"
echo "Login page OK"

echo "3. Testing invalid login..."
curl -s -X POST "$BASE_URL/login" \
  -d "username=notarealuser" \
  -d "password=wrong" | grep -q "Invalid username or password"
echo "Invalid login OK"

echo "4. Testing SQL injection login attempt..."
curl -s -X POST "$BASE_URL/login" \
  -d "username=' OR '1'='1" \
  -d "password=anything" | grep -q "Invalid username or password"
echo "SQL injection login attempt blocked"

echo "5. Testing search page..."
curl -s "$BASE_URL/search" | grep -q "Search Tweets"
echo "Search page OK"

echo "All login/security tests passed."
