#!/bin/bash
set -e
BASE="http://localhost:8888"

echo "1 login page"
curl -s "$BASE/login" | grep -q "Login"
echo "PASS"

echo "2 create account page"
curl -s "$BASE/create_account" | grep -q "Create Account"
echo "PASS"

echo "3 password mismatch"
curl -s -X POST "$BASE/create_account" \
  -d "username=test_mismatch_12345" \
  -d "password1=abc" \
  -d "password2=def" | grep -q "Passwords do not match"
echo "PASS"

echo "4 duplicate username"
curl -s -X POST "$BASE/create_account" \
  -d "username=daisy" \
  -d "password1=abc" \
  -d "password2=abc" | grep -q "Username already exists"
echo "PASS"

echo "5 search weird symbols no crash"
curl -s "$BASE/search?query=%28%28%28%28%28&page=0" | grep -q "Search Results"
echo "PASS"

echo "6 search nonnumeric page no crash"
curl -s "$BASE/search?query=data&page=abc" | grep -q "Search Results"
echo "PASS"

echo "Extra tests passed."
