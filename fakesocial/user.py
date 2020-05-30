"""
"""

import logging
import random

from . import bio
from . import data
from . import image
from . import post


images_dir = "images"


def _get_unused_image():
    session = data.Session()

    used_uuids_q = session.query(data.User.image_uuid)
    all_uuids_q = session.query(data.Image.uuid)
    unused_uuids_q = all_uuids_q.filter(data.Image.uuid.notin_(used_uuids_q))

    if unused_uuids_q.count() == 0:
        logging.debug("no unused images")
        return
    else:
        image_uuid = unused_uuids_q.first()[0]
        logging.debug("{} -> using unused image".format(image_uuid))
        return image_uuid


def gen_user(created_date=None):
    image_uuid = _get_unused_image() or image.get_new_image()
    full_name = bio.gen_full_name()
    location = bio.gen_location()
    job_title = bio.gen_job_title() or bio.get_random_job_title()
    company_name = bio.gen_company_name()

    user = data.User(
        created_date=created_date,
        image_uuid=image_uuid,
        full_name=full_name,
        location=location,
        job_title=job_title,
        company_name=company_name,
    )

    session = data.Session()
    session.add(user)
    session.commit()

    return user


def get_random_user():
    session = data.Session()
    user_ids = [row[0] for row in session.query(data.User.id).all()]
    return random.choice(user_ids)


@data.retry_if_constraint_fails
def create_random_user_connection(created_date=None):
    session = data.Session()
    if session.query(data.User.id).count() < 2:
        raise ValueError("Not enough users to create connection")

    user_1 = get_random_user()
    user_2 = user_1
    while user_2 == user_1:
        user_2 = get_random_user()

    user_1_id = min(user_1, user_2)
    user_2_id = max(user_1, user_2)

    connection = data.Connection(
        created_date=created_date, user_1_id=user_1_id, user_2_id=user_2_id
    )

    session.add(connection)
    session.commit()

    return (user_1_id, user_2_id)


@data.retry_if_constraint_fails
def create_random_post_like(user_id=None, post_id=None, created_date=None):
    session = data.Session()

    post_id = post_id or post.get_random_post()
    user_id = user_id or get_random_user()

    like = data.Like(created_date=created_date, post_id=post_id, user_id=user_id)

    session = data.Session()
    session.add(like)
    session.commit()

    return like
