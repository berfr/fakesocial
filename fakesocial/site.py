"""
"""

import datetime
import distutils.dir_util
import json
import logging
import os
import pathlib
import shutil

import PIL.Image

from . import config
from . import data
from . import image


site_data_dir = "{}/data".format(config.config["output_dir"])
site_images_dir = "{}/images".format(config.config["output_dir"])
site_data_posts_dir = "{}/data/posts".format(config.config["output_dir"])
site_data_users_dir = "{}/data/users".format(config.config["output_dir"])
posts_file = "posts.json"
users_file = "users.json"

json_indent = 4 if os.environ.get("DEBUG") else None


def setup_site_dir():
    if not os.path.exists(config.config["output_dir"]):
        os.mkdir(config.config["output_dir"])
    for filename in os.listdir(config.config["output_dir"]):
        if filename != ".git":
            filepath = "{}/{}".format(config.config["output_dir"], filename)
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                os.remove(filepath)
    distutils.dir_util.copy_tree("static", config.config["output_dir"])
    pathlib.Path(config.config["output_dir"], "images").mkdir(
        parents=True, exist_ok=True
    )
    pathlib.Path(config.config["output_dir"], "data", "users").mkdir(
        parents=True, exist_ok=True
    )
    pathlib.Path(config.config["output_dir"], "data", "posts").mkdir(
        parents=True, exist_ok=True
    )


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.strftime("%Y-%m-%d %H:%M")


def gen_posts_data():
    logging.info("generating site posts data")
    posts_per_page = 25
    current_page = []
    current_page_number = 1

    session = data.Session()
    posts = session.query(data.Post).order_by(data.Post.created_date).all()
    for i, p in enumerate(posts, start=1):
        with open("{}/{}.json".format(site_data_posts_dir, p.id), "w+") as f:
            json.dump(p.details(), f, indent=json_indent, default=myconverter)

        current_page.append(p.info())
        if i % posts_per_page == 0 or i == len(posts):
            current_page_d = {"posts": current_page}
            if current_page_number > 1:
                current_page_d["previous_page"] = "/data/posts-{}.json".format(
                    current_page_number - 1
                )
            if len(posts) - i >= posts_per_page:
                current_page_d["next_page"] = "/data/posts-{}.json".format(
                    current_page_number + 1
                )
            with open(
                "{}/posts-{}.json".format(site_data_dir, current_page_number), "w+"
            ) as f:
                json.dump(current_page_d, f, indent=json_indent, default=myconverter)
            current_page = []
            current_page_number += 1

    posts_pages_info = {
        "first_page": "/data/posts-1.json",
        "last_page": "/data/posts-{}.json".format(current_page_number - 1),
        "posts_per_page": posts_per_page,
    }
    with open("{}/{}".format(site_data_dir, posts_file), "w+") as f:
        json.dump(posts_pages_info, f, indent=json_indent)


def gen_users_data():
    logging.info("generating site users data")
    session = data.Session()

    for u in session.query(data.User).order_by(data.User.id).all():
        with open("{}/{}.json".format(site_data_users_dir, u.id), "w+") as f:
            json.dump(u.details(), f, indent=json_indent, default=myconverter)


def gen_images():
    logging.info("generating site images")
    session = data.Session()

    for i in session.query(data.Image).all():
        image_path = image._get_image_path(i.uuid)

        dest_file_name = "{}/{}".format(site_images_dir, i.uuid)

        im = PIL.Image.open(image_path)

        im_64 = im.resize((64, 64))
        im_64.save("{}_64.jpg".format(dest_file_name))

        im_256 = im.resize((256, 256))
        im_256.save("{}_256.jpg".format(dest_file_name))


def get_stats():
    session = data.Session()
    stats = {
        "user_count": session.query(data.User).count(),
        "post_count": session.query(data.Post).count(),
        "image_count": session.query(data.Image).count(),
        "connection_count": session.query(data.Connection).count(),
        "connection_count": session.query(data.Connection).count(),
        "comment_count": session.query(data.Comment).count(),
        "like_count": session.query(data.Like).count(),
    }
    stats["total_events"] = (
        stats["user_count"]
        + stats["post_count"]
        + stats["connection_count"]
        + stats["connection_count"]
        + stats["comment_count"]
        + stats["like_count"]
    )
    return stats
