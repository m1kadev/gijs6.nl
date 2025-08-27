#!/bin/bash
set -e

BASE_DIR="$(dirname "$(realpath "$0")")"

git -C "$BASE_DIR" fetch
echo "Fetched"

git -C "$BASE_DIR" reset --hard "@{u}"
echo "Updated files"

touch /var/www/www_gijs6_nl_wsgi.py
echo "Redeployed page"
