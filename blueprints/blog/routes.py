from flask import (
    Blueprint,
    render_template,
    Response,
    request,
    make_response,
    abort,
)
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
import subprocess
import os
import commonmark
import yaml
import pytz
import re
import hashlib

blog_bp = Blueprint(
    "blog_bp", __name__, template_folder="templates", static_folder="static"
)

BASE_DIR = os.path.dirname(__file__)

CACHED_POST_LIST = []
CACHED_POSTS = {}
CACHED_FEED = {}
CACHED_LAST_MODIFIED = None
CACHED_ARCHIVED_POST_LIST = []
CACHED_ARCHIVED_POSTS = {}


def generate_html(md_input):
    pattern = r"%ref%(.*?)%ref%"
    refs = []
    ref_number = 0

    def parse_refs(match):
        nonlocal ref_number
        content = match.group(1)
        title, url = content.split("-#-")
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


def load_posts_from_directory(posts_dir, url_prefix=""):
    post_list = []
    posts_dict = {}
    posts_data = []

    for post_file in os.listdir(posts_dir):
        if not post_file.endswith(".md"):
            continue

        file_path = os.path.join(posts_dir, post_file)
        with open(file_path) as file:
            file_content = file.read().strip()

        extract = re.match(r"^---\n(.*?)\n---\n", file_content, re.DOTALL)
        post_data = yaml.safe_load(extract.group(1))
        slug = post_file.removesuffix(".md")
        post_data["url"] = url_prefix + "/" + slug

        lines = (
            subprocess.check_output(
                [
                    "git",
                    "log",
                    "--follow",
                    "--format=%H %ct",
                    "--",
                    f"{os.path.relpath(posts_dir, BASE_DIR)}/{post_file}",
                ],
                text=True,
                cwd=BASE_DIR,
            )
            .strip()
            .split("\n")
        )
        try:
            first_commit = lines[-1].split()
            last_commit = lines[0].split()
            first_commit_ts = int(first_commit[1])
            last_commit_ts = int(last_commit[1])
            first_commit_dt = datetime.fromtimestamp(first_commit_ts, tz=timezone.utc)
            last_commit_dt = datetime.fromtimestamp(last_commit_ts, tz=timezone.utc)
            post_data["date"] = first_commit_dt.strftime("%d-%m-%Y")
            post_data["date_iso"] = first_commit_dt.isoformat()
            post_data["timestamp"] = first_commit_ts
            post_info = {
                "latest_commit": {
                    "hash": last_commit[0],
                    "datetime": last_commit_dt.strftime("%d-%m-%Y at %H:%M:%S"),
                    "datetime_iso": last_commit_dt.isoformat(),
                },
                "first_commit": {
                    "hash": first_commit[0],
                    "datetime": first_commit_dt.strftime("%d-%m-%Y at %H:%M:%S"),
                    "datetime_iso": first_commit_dt.isoformat(),
                },
                "multiple_edit": last_commit[0] != first_commit[0],
            }
        except Exception:
            post_data["date"] = "Not yet published"
            post_data["timestamp"] = float("inf")
            post_info = {
                "latest_commit": {"datetime": "unknown"},
                "first_commit": {"datetime": "unknown"},
            }
            first_commit_ts = last_commit_ts = int(
                datetime.now(tz=timezone.utc).timestamp()
            )

        file_content_clean = re.sub(
            r"^---\s*\n.*?\n---\s*\n", "", file_content, flags=re.DOTALL
        )
        html_content = generate_html(file_content_clean)

        posts_dict[slug] = {
            "blog_content": html_content,
            **post_data,
            **post_info,
        }

        post_list.append(post_data)

        posts_data.append(
            {
                "title": post_data.get("title", "Untitled"),
                "slug": slug,
                "pub_date": datetime.fromtimestamp(first_commit_ts, tz=pytz.UTC),
                "updated_date": datetime.fromtimestamp(last_commit_ts, tz=pytz.UTC),
                "content": html_content,
            }
        )

    post_list.sort(key=lambda x: x["timestamp"], reverse=True)
    return post_list, posts_dict, posts_data


def load_posts_into_cache():
    global \
        CACHED_POST_LIST, \
        CACHED_POSTS, \
        CACHED_FEED, \
        CACHED_LAST_MODIFIED, \
        CACHED_ARCHIVED_POST_LIST, \
        CACHED_ARCHIVED_POSTS

    posts_dir = os.path.join(BASE_DIR, "posts")
    post_list, posts_dict, posts_data = load_posts_from_directory(posts_dir, "/blog")
    CACHED_POST_LIST = post_list
    CACHED_POSTS = posts_dict

    archived_dir = os.path.join(BASE_DIR, "archived")
    if os.path.exists(archived_dir):
        archived_list, archived_dict, _ = load_posts_from_directory(
            archived_dir, "/blog/archived"
        )
        CACHED_ARCHIVED_POST_LIST = archived_list
        CACHED_ARCHIVED_POSTS = archived_dict
    else:
        CACHED_ARCHIVED_POST_LIST = []
        CACHED_ARCHIVED_POSTS = {}

    feed = FeedGenerator()
    feed.title("Gijs6 - Blog")
    feed.id("https://www.gijs6.nl/blog")
    feed.link(href="https://www.gijs6.nl/blog/rss.xml", rel="self")
    feed.link(href="https://www.gijs6.nl/blog", rel="alternate")
    feed.description("My own blog")
    feed.author(name="Gijs ten Berg - Gijs6", email="gijs6@dupunkto.org")
    feed.language("en")

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

    CACHED_FEED["rss"] = feed.rss_str(pretty=True)
    CACHED_FEED["atom"] = feed.atom_str(pretty=True)
    CACHED_LAST_MODIFIED = max(
        (post["updated_date"] for post in posts_data), default=datetime.now(pytz.UTC)
    )


@blog_bp.route("/")
def blog_index():
    return render_template("index.html", post_list=CACHED_POST_LIST)


@blog_bp.route("/<string:slug>")
def blog_post(slug):
    post = CACHED_POSTS.get(slug)
    if not post:
        abort(404)
    return render_template("post.html", **post)


@blog_bp.route("/archived")
def archived_index():
    return render_template("archived_index.html", post_list=CACHED_ARCHIVED_POST_LIST)


@blog_bp.route("/archived/<string:slug>")
def archived_post(slug):
    post = CACHED_ARCHIVED_POSTS.get(slug)
    if not post:
        abort(404)
    return render_template("post.html", is_archived=True, **post)


def make_feed_response(feed_type="rss"):
    data = CACHED_FEED[feed_type]
    last_modified = CACHED_LAST_MODIFIED

    # Handle If-Modified-Since header
    if_modified_since = request.headers.get("If-Modified-Since")
    if if_modified_since:
        try:
            client_time = datetime.strptime(
                if_modified_since, "%a, %d %b %Y %H:%M:%S GMT"
            ).replace(tzinfo=timezone.utc)
            if last_modified <= client_time:
                return Response(status=304)
        except Exception:
            pass

    # Generate content hash for ETag
    content_hash = hashlib.sha256(data).hexdigest()[:16]
    etag_value = f'W/"{feed_type}-{content_hash}"'

    # Handle If-None-Match header (ETag)
    if_none_match = request.headers.get("If-None-Match")
    if if_none_match and etag_value in if_none_match:
        return Response(status=304)

    response = make_response(data)
    content_type = (
        "application/xml; charset=utf-8"
        if feed_type == "rss"
        else "application/xml; charset=utf-8"
    )
    response.headers["Content-Type"] = content_type
    response.headers["Last-Modified"] = last_modified.strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    response.headers["Cache-Control"] = "public, max-age=3600"
    response.headers["ETag"] = etag_value
    return response


@blog_bp.route("/rss.xml")
def rss():
    return make_feed_response("rss")


@blog_bp.route("/atom.xml")
def atom():
    return make_feed_response("atom")


load_posts_into_cache()
