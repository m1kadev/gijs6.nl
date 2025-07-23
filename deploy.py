import os
import subprocess

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

subprocess.run(["git", "fetch"], check=True, cwd=BASE_DIR)
print("Fetched")

subprocess.run(["git", "reset", "--hard", "origin/main"], check=True, cwd=BASE_DIR)
print("Updated files")

subprocess.run(["touch", "/var/www/www_gijs6_nl_wsgi.py"], check=True)
print("Redeployed page")
