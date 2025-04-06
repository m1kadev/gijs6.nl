from flask import Blueprint, render_template
import os
import commonmark
import yaml
import re

blog_bp = Blueprint("blog_bp", __name__, template_folder="templates", static_folder="static")

BASE_DIR = os.path.dirname(__file__)


@blog_bp.route("/")
def blog_index():
    post_list = []
    for post in os.listdir(os.path.join(BASE_DIR, "posts")):
        with open(os.path.join(BASE_DIR, "posts", post)) as file:
            file_content = file.read().strip()
        extract = re.match(r'^---\n(.*?)\n---\n', file_content, re.DOTALL)
        post_data = yaml.safe_load(extract.group(1))
        post_data["url"] = "/blog/" + post.removesuffix(".md")
        post_list.append(post_data)
    return render_template("index.html", post_list = post_list)


@blog_bp.route("/<string:title>")
def blog_post(title):
    file_name = title + ".md"
    with open(os.path.join(BASE_DIR, "posts", file_name)) as file:
        file_content = file.read().strip()

    extract = re.match(r'^---\n(.*?)\n---\n', file_content, re.DOTALL)
    post_data = yaml.safe_load(extract.group(1))

    file_content_clean = re.sub(r'^---\s*\n.*?\n---\s*\n', '', file_content, flags=re.DOTALL)

    text = commonmark.commonmark(file_content_clean)
    
    return render_template("post.html", content = text, **post_data)
