from flask import Blueprint, render_template, redirect, url_for, Response
from datetime import datetime
from feedgen.feed import FeedGenerator
import subprocess
import os
import commonmark
import yaml
import pytz
import html
import re

blog_bp = Blueprint("blog_bp", __name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(__file__)


@blog_bp.route("/")
def blog_index():
    post_list = []
    for post in os.listdir(os.path.join(BASE_DIR, "posts")):
        with open(os.path.join(BASE_DIR, "posts", post)) as file:
            file_content = file.read().strip()
        extract = re.match(r"^---\n(.*?)\n---\n", file_content, re.DOTALL)
        post_data = yaml.safe_load(extract.group(1))
        post_data["url"] = "/blog/" + post.removesuffix(".md")
        lines = subprocess.check_output(["git", "log", "--format=%H %ct", "--", f"bps/blog/posts/{post}"], text=True).strip().split("\n")
        try:
            post_data["date"] = datetime.fromtimestamp(int(lines[-1].split()[1])).strftime("%d-%m-%Y")
        except:
            post_data["date"] = "lol"
        post_list.append(post_data)
    return render_template("index.html", post_list = post_list)


@blog_bp.route("/<string:title>")
def blog_post(title):
    file_name = title + ".md"
    try:
        with open(os.path.join(BASE_DIR, "posts", file_name)) as file:
            file_content = file.read().strip()
    except FileNotFoundError:
        return redirect(url_for("blog_bp.blog_index"))
    
    lines = subprocess.check_output(["git", "log", "--format=%H %ct", "--", f"bps/blog/posts/{file_name}"], text=True).strip().split("\n")

    post_info = {
        "latest_commit": {
            "hash": lines[0].split()[0],
            "datetime": datetime.fromtimestamp(int(lines[0].split()[1])).strftime("%d-%m-%Y at %H:%M:%S")
        },
        "first_commit": {
            "hash": lines[-1].split()[0],
            "datetime": datetime.fromtimestamp(int(lines[-1].split()[1])).strftime("%d-%m-%Y at %H:%M:%S")
        }
    }

    extract = re.match(r"^---\n(.*?)\n---\n", file_content, re.DOTALL)
    post_data = yaml.safe_load(extract.group(1))

    file_content_clean = re.sub(r"^---\s*\n.*?\n---\s*\n", "", file_content, flags=re.DOTALL)

    text = commonmark.commonmark(file_content_clean)
    
    return render_template("post.html", content = text, **post_data, **post_info)



# Function to generate an RSS feed
def generate_rss_feed():
    feed = FeedGenerator()
    feed.title("Gijs6 - Blog")
    feed.link(href="http://gijs6.nl/blog", rel="self")
    feed.description("My own blog")

    for post in os.listdir(os.path.join(BASE_DIR, "posts")):
        try:
            lines = subprocess.check_output(["git", "log", "--format=%H %ct", "--", f"bps/blog/posts/{post}"], text=True).strip().split("\n")
            date = datetime.fromtimestamp(int(lines[-1].split()[1]), pytz.timezone('Europe/Amsterdam'))
        except IndexError:
            continue

        with open(os.path.join(BASE_DIR, "posts", post)) as file:
            file_content = file.read().strip()
        extract = re.match(r"^---\n(.*?)\n---\n", file_content, re.DOTALL)
        post_data = yaml.safe_load(extract.group(1))

        title = post_data.get("title", "Untitled")
        slug = post.removesuffix(".md")

        file_content_clean = re.sub(r"^---\s*\n.*?\n---\s*\n", "", file_content, flags=re.DOTALL)

        html_content = html.escape(commonmark.commonmark(file_content_clean))

        entry = feed.add_entry()
        entry.title(title)
        entry.link(href=f"http://gijs6.nl/blog/{slug}")
        entry.description(html_content)
        entry.pubDate(date)

    return feed.rss_str()

@blog_bp.route("/rss.xml")
def rss():
    rss_feed = generate_rss_feed()
    return Response(rss_feed, mimetype="application/xml")
