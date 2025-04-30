---
title: Modular Flask
---

# Building a Modular Website with Flask

This site and this blog you're readintg is built using the *amazing* Python framework **Flask**. And yeah, I do mean amazing. It's simple, lightweight, flexible, and lets you get going super fast. But despite all that, for a long time, my site was... well, kind of a mess.

See, I was managing a bunch of different projects on the same domain. Some blog stuff here, some API endpoints there and some random private school dasboard pages. It worked, technically. But maintaining it? *Absolute pain.*

I knew I needed something modular. Something that didn't involve scrolling through 1400 lines of spaghetti in one single Python file. And thankfully, Flask already had the perfect solution: **blueprints**.

## Before Blueprints

My old `main.py` was a single 1400-line mess. A mix of routes, logic, utilities and way to many print statments. There was *no* structure. Every new route was just tacked on wherever I happened to have the cursor.

## Enter: Flask Blueprints

Blueprints are basically Flask's way of saying: "Hey, maybe split this up a bit?" They let you group routes and logic into objects that work really similar to the `app`-object. Think of them as little mini `app`-objects that plug into your main app.

All the endpoints in a blueprint are registered with the blueprint itself, and then that blueprint gets registered *with your main app*.

Here's the most basic example:

`blueprints/simple.py`

```python
from flask import Blueprint

simple_bp = Blueprint("simple_bp", __name__, template_folder="templates")

@simple_bp.route("/")
def index():
    return "Hello world!"
```

Then over in `app.py`, you just plug it in:

```python
from flask import Flask
from blueprints.simple import simple_bp

app = Flask(__name__)
app.register_blueprint(simple_bp, url_prefix="/simple")
```

And then your page is avaiable under `/simple/`!

## Making It Scalable

Manually importing each blueprint works fine when you only have a couple. But once you start scaling things up, this gets tedious quite fast.

So I wrote a tiny bit of automation to handle this. It walks through all subfolders in the `blueprints/` folder, looks for a `routes.py` file, and tries to import a `*_bp` object from it.

Here's what that looks like:

`blueprints/__init__.py`

```python
import os
import importlib

def load_blueprints():
    blueprints = []
    base_path = os.path.dirname(__file__)

    for file_item in os.scandir(base_path):
        if file_item.is_dir():
            routes_path = os.path.join(file_item.path, "routes.py")
            if os.path.isfile(routes_path):
                module_path = f"blueprints.{file_item.name}.routes"
                try:
                    module = importlib.import_module(module_path)

                    for attr in dir(module):
                        if attr.endswith("_bp"):
                            bp = getattr(module, attr)
                            blueprints.append((bp, f"/{file_item.name}"))
                except Exception as e:
                    print(f"An error occurred while trying to load {module_path}: {e}")

    return blueprints
```

And then your `app.py` gets way cleaner:

```python
from flask import Flask
from blueprints import load_blueprints

app = Flask(__name__)

# Register all blueprints automatically
for bp, prefix in load_blueprints():
    try:
        app.register_blueprint(bp, url_prefix=prefix)
    except Exception as e:
        print(f"An error occurred while trying to load {bp} as a blueprint: {e}")
```

And the URl prefixes are just based on the folder names, so you don't have to declare names everywhere.

## Final thoughts

If you're using Flask for anything complex, just use blueprints. Don't wait until you have huge single Python file that somehow became your entire backend.

Modularizing your Flask project doesn't just make the code cleaner, it makes it more enjoyable to work on. Which, if you've ever had to debug an endpoint in a 1.4k-line Python file, you know is kind of a big deal.
