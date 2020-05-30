"""
"""

import logging
import os
import pathlib
import urllib.request
import uuid
import time
import hashlib

import PIL.Image

from . import data


images_url = "https://thispersondoesnotexist.com/image"
images_dir = "images"
images_dimensions = (256, 256)


def _get_new_uuid():
    while True:
        u = str(uuid.uuid4())[:8]
        if os.path.exists(_get_image_path(u)):
            continue
        return u


def _image_hash(image_uuid):
    image_path = _get_image_path(image_uuid)
    with open(image_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _get_image_path(image_uuid):
    return "{}/{}.jpg".format(images_dir, image_uuid)


def _fetch_image():
    req = urllib.request.Request(images_url)
    req.add_header("User-Agent", "firefox")
    r = urllib.request.urlopen(req)

    image_uuid = _get_new_uuid()
    image_path = _get_image_path(image_uuid)

    im = PIL.Image.open(r).resize(images_dimensions)
    im.save(image_path)

    return image_uuid


def get_new_image():
    while True:
        image_uuid = _fetch_image()
        image_path = _get_image_path(image_uuid)
        image_hash = _image_hash(image_uuid)

        session = data.Session()
        registered_hashes = [
            row[0] for row in session.query(data.Image.image_hash).all()
        ]

        if image_hash in registered_hashes:
            logging.debug("fetched image already registered")
            os.remove(image_path)
            time.sleep(0.5)
            continue

        logging.debug("{} -> fetched new image".format(image_uuid))
        _register_image(image_uuid)

        return image_uuid


def _resize_image(image_uuid):
    image_path = _get_image_path(image_uuid)
    im = PIL.Image.open(image_path)

    if im.size == images_dimensions:
        logging.debug("{} -> correct dimensions".format(image_uuid))
        return

    logging.debug("{} -> resizing image".format(image_uuid))
    new_im = im.resize(images_dimensions)
    new_im.save(image_path)


def _register_image(image_uuid, delete_if_exists=False):
    session = data.Session()

    registered_uuids = [row[0] for row in session.query(data.Image.uuid).all()]
    if image_uuid in registered_uuids:
        logging.debug("{} -> uuid already registered")
        return

    _resize_image(image_uuid)
    image_path = _get_image_path(image_uuid)
    image_hash = _image_hash(image_uuid)

    registered_hashes = [row[0] for row in session.query(data.Image.image_hash).all()]
    if image_hash in registered_hashes:
        logging.debug("{} -> hash already registered".format(image_uuid))
        if delete_if_exists:
            logging.debug("{} -> deleting image".format(image_uuid))
            os.remove(image_path)
        return

    image = data.Image(uuid=image_uuid, image_hash=image_hash)

    logging.debug("{} -> registering new image".format(image_uuid))
    session = data.Session()
    session.add(image)
    session.commit()


def register_images(delete_duplicates=False):
    logging.info("registering images")
    for file_name in os.listdir(images_dir):
        file_uuid = pathlib.Path(file_name).stem
        _register_image(file_uuid, delete_duplicates)
