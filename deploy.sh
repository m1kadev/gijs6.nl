#!/bin/bash
set -e

BASE_DIR="$(dirname "$(realpath "$0")")"

git -C "$BASE_DIR" fetch
echo "Fetched latest git commit."

git -C "$BASE_DIR" reset --hard "@{u}"
echo "Updated repo to match latest git commit"

touch /var/www/www_gijs6_nl_wsgi.py
echo "Touched WSGI file"
