"""
"""

import csv
import logging
import random

import markovify
import sqlalchemy

from . import data
from . import user


quote_file = "data/QUOTE.csv"
quote_model = None


def _capitalize_first_letter(text):
    if text:
        return text[0].upper() + text[1:]
    else:
        return text


def _capitalize_sentences(text):
    punctuations = set(".?!")
    result = text
    for p in punctuations:
        a = [_capitalize_first_letter(s.strip()) for s in result.split(p)]
        result = "{} ".format(p).join(a).strip()
    return result


def _gen_quote(length=200):
    global quote_model
    if not quote_model:
        with open(quote_file) as f:
            reader = csv.reader(f)
            quotes = "\n".join([row[1] for row in reader])
            quote_model = markovify.NewlineText(quotes, well_formed=False).compile()
    quote = quote_model.make_short_sentence(length, tries=1000)
    quote = _capitalize_sentences(quote)
    logging.debug("generated quote")
    return quote


def _gen_text():
    return _gen_quote()


def gen_post(user_id=None, created_date=None):
    user_id = user_id or user.get_random_user()
    text = _gen_text()

    post = data.Post(created_date=created_date, user_id=user_id, text=text)

    session = data.Session()
    session.add(post)
    session.commit()

    return post


def get_random_recent_post():
    session = data.Session()
    posts = (
        session.query(data.Post)
        .order_by(sqlalchemy.desc(data.Post.created_date))
        .limit(5)
        .all()
    )
    return random.choice(posts).id


def gen_comment(user_id=None, post_id=None, created_date=None):
    user_id = user_id or user.get_random_user()
    post_id = post_id or get_random_recent_post()
    text = _gen_quote(length=50)

    comment = data.Comment(
        created_date=created_date, user_id=user_id, post_id=post_id, text=text,
    )

    session = data.Session()
    session.add(comment)
    session.commit()

    return comment
