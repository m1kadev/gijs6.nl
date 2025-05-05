from flask import Blueprint, render_template, redirect, url_for, Response
from datetime import datetime
from feedgen.feed import FeedGenerator
import subprocess
import os
import commonmark
import yaml
import pytz
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

        if not post_data.get("date"):
            lines = subprocess.check_output(["git", "log", "--format=%ct", "--", f"posts/{post}"], text=True, cwd=BASE_DIR).strip().split("\n")
            try:
                timestamp = int(lines[-1])
                post_data["date"] = datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y")
                post_data["timestamp"] = timestamp  # for sorting
            except (ValueError, IndexError):
                post_data["date"] = "Not yet published"
                post_data["timestamp"] = float("inf")
        else:
            dt = datetime.strptime(str(post_data["date"]), "%Y-%m-%d")
            post_data["date"] = dt.strftime("%d-%m-%Y")
            post_data["timestamp"] = int(dt.timestamp())

        post_list.append(post_data)

    post_list.sort(key=lambda x: x["timestamp"], reverse=True)

    return render_template("index.html", post_list = post_list)


def generate_html(md_input):
    pattern = r"%ref%(.*?)%ref%"

    refs = []

    ref_number = 0

    def parse_refs(match):
        nonlocal ref_number
        content = match.group(1)
        content_split = content.split("-#-")
        title = content_split[0]
        url = content_split[1]
        ref_number += 1
        refs.append({"title": title, "url": url, "number": ref_number})
        return f"<a class='ref-inline' href='#ref-url-{ref_number}'>[{ref_number}]</a>"

    md_input = re.sub(pattern, parse_refs, md_input)

    html_output = "<article>" + commonmark.commonmark(md_input) + "</article>"

    if refs:
        return (
            html_output
            + "<section id='refs'><h2>References</h2><ol>"
            + "".join(
                f"<li><a id='ref-url-{item['number']}' href='{item['url']}'>{re.sub(r'</?p>', '', commonmark.commonmark(item['title']))}</a></li>"
                for item in refs
            )
            + "</ol></section>"
        )

    return html_output


@blog_bp.route("/<string:slug>")
def blog_post(slug):
    file_name = slug + ".md"
    try:
        with open(os.path.join(BASE_DIR, "posts", file_name)) as file:
            file_content = file.read().strip()
    except FileNotFoundError:
        return redirect(url_for("blog_bp.blog_index"))

    lines = subprocess.check_output(["git", "log", "--format=%H %ct", "--", f"posts/{file_name}"], text=True, cwd=BASE_DIR).strip().split("\n")
    try:
        post_info = {
            "latest_commit": {
                "hash": lines[0].split()[0],
                "datetime": datetime.fromtimestamp(int(lines[0].split()[1])).strftime("%d-%m-%Y at %H:%M:%S")
            },
            "first_commit": {
                "hash": lines[-1].split()[0],
                "datetime": datetime.fromtimestamp(int(lines[-1].split()[1])).strftime("%d-%m-%Y at %H:%M:%S")
            },
            "multiple_edit": lines[0].split()[0] != lines[-1].split()[0]
        }
    except (ValueError, IndexError):
        post_info = {
            "latest_commit": {
                "datetime": "unknown"
            },
            "first_commit": {
                "datetime": "unknown"
            }
        }

    extract = re.match(r"^---\n(.*?)\n---\n", file_content, re.DOTALL)
    post_data = yaml.safe_load(extract.group(1))

    file_content_clean = re.sub(r"^---\s*\n.*?\n---\s*\n", "", file_content, flags=re.DOTALL)

    text = generate_html(file_content_clean)

    return render_template("post.html", blog_content = text, **post_data, **post_info)


def generate_rss_feed():
    feed = FeedGenerator()
    feed.title("Gijs6 - Blog")
    feed.id("http://www.gijs6.nl/blog")
    feed.link(href="http://www.gijs6.nl/blog/rss.xml", rel="self", type="application/rss+xml")
    feed.link(href="http://www.gijs6.nl/blog/atom.xml", rel="self", type="application/atom+xml")
    feed.description("My own blog")
    feed.author(name="Gijs ten Berg - Gijs6", email="gijs6@dupunkto.org")
    feed.language("en")

    posts_data = []

    for post in os.listdir(os.path.join(BASE_DIR, "posts")):
        with open(os.path.join(BASE_DIR, "posts", post)) as file:
            file_content = file.read().strip()
        extract = re.match(r"^---\n(.*?)\n---\n", file_content, re.DOTALL)
        post_data = yaml.safe_load(extract.group(1))

        title = post_data.get("title", "Untitled")
        slug = post.removesuffix(".md")

        file_content_clean = re.sub(r"^---\s*\n.*?\n---\s*\n", "", file_content, flags=re.DOTALL)

        if post_data.get("date"):
            date = datetime.fromisoformat(str(post_data["date"])).astimezone(pytz.timezone("Europe/Amsterdam"))
            timestamp = date.timestamp()
        else:
            try:
                lines = subprocess.check_output(["git", "log", "--format=%ct", "--", f"posts/{post}"], text=True, cwd=BASE_DIR).strip().split("\n")
                date = datetime.fromtimestamp(int(lines[-1]), pytz.timezone("Europe/Amsterdam"))
                timestamp = int(lines[-1])
            except (ValueError, IndexError):
                # Not published posts
                continue

        html_content = generate_html(file_content_clean)

        posts_data.append({
            "title": title,
            "slug": slug,
            "date": date,
            "timestamp": timestamp,
            "description": html_content
        })

    # Sort posts by date
    posts_data = sorted(posts_data, key=lambda x: x["timestamp"])

    # Add to feed
    for post in posts_data:
        entry = feed.add_entry()
        entry.title(post["title"])
        entry.id(f"https://www.gijs6.nl/blog/{post['slug']}")
        entry.link(href=f"https://www.gijs6.nl/blog/{post['slug']}")
        entry.content(post["description"], type="html")
        entry.pubDate(post["date"])
        entry.author(name="Gijs ten Berg - Gijs6", email="gijs6@dupunkto.org")

    return feed


@blog_bp.route("/rss.xml")
def rss():
    feed = generate_rss_feed()
    rss_feed = feed.rss_str(pretty=True)
    return Response(rss_feed, mimetype="application/xml; charset=utf-8")

@blog_bp.route("/atom.xml")
def atom():
    feed = generate_rss_feed()
    atom_feed = feed.atom_str(pretty=True)
    return Response(atom_feed, mimetype="application/xml; charset=utf-8")
