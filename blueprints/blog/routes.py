from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    Response,
    request,
    make_response,
)
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import subprocess
import os
import commonmark
import yaml
import pytz
import re

blog_bp = Blueprint(
    "blog_bp", __name__, template_folder="templates", static_folder="static"
)

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

        lines = (
            subprocess.check_output(
                ["git", "log", "--format=%ct", "--", f"posts/{post}"],
                text=True,
                cwd=BASE_DIR,
            )
            .strip()
            .split("\n")
        )
        try:
            timestamp = int(lines[-1])
            post_data["date"] = datetime.fromtimestamp(timestamp).strftime(
                "%d-%m-%Y"
            )
            post_data["timestamp"] = timestamp  # for sorting
        except (ValueError, IndexError):
            post_data["date"] = "Not yet published"
            post_data["timestamp"] = float("inf")

        post_list.append(post_data)

    post_list.sort(key=lambda x: x["timestamp"], reverse=True)

    return render_template("index.html", post_list=post_list)


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

    lines = (
        subprocess.check_output(
            ["git", "log", "--format=%H %ct", "--", f"posts/{file_name}"],
            text=True,
            cwd=BASE_DIR,
        )
        .strip()
        .split("\n")
    )
    try:
        post_info = {
            "latest_commit": {
                "hash": lines[0].split()[0],
                "datetime": datetime.fromtimestamp(int(lines[0].split()[1])).strftime(
                    "%d-%m-%Y at %H:%M:%S"
                ),
            },
            "first_commit": {
                "hash": lines[-1].split()[0],
                "datetime": datetime.fromtimestamp(int(lines[-1].split()[1])).strftime(
                    "%d-%m-%Y at %H:%M:%S"
                ),
            },
            "multiple_edit": lines[0].split()[0] != lines[-1].split()[0],
        }
    except (ValueError, IndexError):
        post_info = {
            "latest_commit": {"datetime": "unknown"},
            "first_commit": {"datetime": "unknown"},
        }

    extract = re.match(r"^---\n(.*?)\n---\n", file_content, re.DOTALL)
    post_data = yaml.safe_load(extract.group(1))

    file_content_clean = re.sub(
        r"^---\s*\n.*?\n---\s*\n", "", file_content, flags=re.DOTALL
    )

    text = generate_html(file_content_clean)

    return render_template("post.html", blog_content=text, **post_data, **post_info)


def generate_rss_feed():
    feed = FeedGenerator()
    feed.title("Gijs6 - Blog")
    feed.id("https://www.gijs6.nl/blog")
    feed.link(href="https://www.gijs6.nl/blog/rss.xml", rel="self")
    feed.link(href="https://www.gijs6.nl/blog", rel="alternate")
    feed.description("My own blog")
    feed.author(name="Gijs ten Berg - Gijs6", email="gijs6@dupunkto.org")
    feed.language("en")

    posts_data = []

    for post_file in os.listdir(os.path.join(BASE_DIR, "posts")):
        if not post_file.endswith(".md"):
            continue

        with open(os.path.join(BASE_DIR, "posts", post_file)) as f:
            content = f.read().strip()
        extract = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        meta = yaml.safe_load(extract.group(1))

        slug = post_file.removesuffix(".md")
        title = meta.get("title", "Untitled")

        body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", content, flags=re.DOTALL)
        html_content = generate_html(body)

        try:
            lines = (
                subprocess.check_output(
                    ["git", "log", "--format=%ct", "--", f"posts/{post_file}"],
                    text=True,
                    cwd=BASE_DIR,
                )
                .strip()
                .split("\n")
            )
            first_commit_ts = int(lines[-1])
            last_commit_ts = int(lines[0])
        except (ValueError, IndexError):
            first_commit_ts = last_commit_ts = int(
                datetime.now(tz=timezone.utc).timestamp()
            )

        pub_date = datetime.fromtimestamp(first_commit_ts, tz=pytz.UTC)
        updated_date = datetime.fromtimestamp(last_commit_ts, tz=pytz.UTC)

        posts_data.append(
            {
                "title": title,
                "slug": slug,
                "pub_date": pub_date,
                "updated_date": updated_date,
                "content": html_content,
            }
        )

    posts_data.sort(key=lambda x: x["pub_date"])

    for post in posts_data:
        entry = feed.add_entry()
        entry.id(f"https://www.gijs6.nl/blog/{post['slug']}")
        entry.title(post["title"])
        entry.link(href=f"https://www.gijs6.nl/blog/{post['slug']}")
        entry.content(post["content"], type="html")
        entry.pubDate(post["pub_date"])
        entry.updated(post["updated_date"])
        entry.author(name="Gijs ten Berg - Gijs6", email="gijs6@dupunkto.org")

    last_modified = max(
        (post["updated_date"] for post in posts_data), default=datetime.now(pytz.UTC)
    )
    return feed, last_modified


def make_feed_response(feed_type="rss"):
    feed, last_modified = generate_rss_feed()

    if_modified_since = request.headers.get("If-Modified-Since")
    if if_modified_since:
        try:
            client_time = datetime.strptime(
                if_modified_since, "%a, %d %b %Y %H:%M:%S GMT"
            )
            client_time = client_time.replace(tzinfo=timezone.utc)
            if last_modified <= client_time:
                return Response(status=304)
        except Exception:
            pass

    if feed_type == "atom":
        data = feed.atom_str(pretty=True)
    else:
        data = feed.rss_str(pretty=True)

    response = make_response(data)
    response.headers["Content-Type"] = "application/xml; charset=utf-8"
    response.headers["Last-Modified"] = last_modified.strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@blog_bp.route("/rss.xml")
def rss():
    return make_feed_response("rss")


@blog_bp.route("/atom.xml")
def atom():
    return make_feed_response("atom")
