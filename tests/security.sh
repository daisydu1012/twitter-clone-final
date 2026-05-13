#!/bin/bash
set -e
BASE="http://localhost:8888"

echo "1 homepage"
curl -s "$BASE/" | grep -q "Twitter Clone"
echo "PASS"

echo "2 invalid login"
curl -s -X POST "$BASE/login" -d "username=not_real_user" -d "password=wrong" | grep -qi "invalid"
echo "PASS"

echo "3 SQL injection login"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/login" -d "username=' OR '1'='1" -d "password=wrong")
test "$STATUS" != "302"
echo "PASS"

echo "4 search injection no crash"
curl -s "$BASE/search?query=%27%20OR%20%271%27%3D%271&page=0" | grep -q "Search Results"
echo "PASS"

echo "5 typo suggestion"
curl -s "$BASE/search?query=datta&page=0" | grep -q "Did you mean"
echo "PASS"

echo "6 bad page no crash"
curl -s "$BASE/?page=abc" | grep -q "Twitter Clone"
echo "PASS"

echo "All tests passed."
