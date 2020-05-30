"""
"""

import argparse
import datetime
import logging
import random

from . import config


parser = argparse.ArgumentParser(description="Generate fakesocial content and website.")

parser.add_argument("--verbose", "-v", action="store_true")
parser.add_argument("--debug", "-d", action="store_true")

parser.add_argument("--config-file", help="Specify JSON config file to load.")
parser.add_argument(
    "--config", "-c", nargs="+", help="Pass list of config key=value pairs."
)

args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.INFO)

if args.debug:
    logging.basicConfig(level=logging.DEBUG)

if args.config_file:
    config.load_config_file(args.config_file)

if args.config:
    for config_string in args.config:
        k, v = config_string.split("=")
        config.config[k] = v

from . import data

latest_created_date = data.get_latest_created_date()
if latest_created_date:
    config.config["start_date"] = latest_created_date
elif config.config.get("start_date"):
    config.config["start_date"] = datetime.datetime.fromisoformat(
        config.config["start_date"]
    )
else:
    config.config["start_date"] = None

logging.info("config: {}".format(config.config))

from . import image
from . import post
from . import site
from . import user

site.setup_site_dir()
image.register_images()

events = [
    user.gen_user,
    *[post.gen_post] * 5,
    *[post.gen_comment] * 10,
    *[user.create_random_user_connection] * 15,
    *[user.create_random_post_like] * 20,
]


def get_created_dates(start_date, end_date, num_events):
    created_dates = []
    seconds_between_dates = int((end_date - start_date).total_seconds())
    distance_between_each = seconds_between_dates // num_events
    for i in range(num_events):
        seconds_occurrence = i * distance_between_each + random.randint(
            1, distance_between_each
        )
        datetime_occurrence = start_date + datetime.timedelta(0, seconds_occurrence)
        created_dates.append(datetime_occurrence)
    return created_dates


def random_event(created_date=None):
    while True:
        event = random.choice(events)
        try:
            return event(created_date=created_date)
        except Exception as e:
            logging.debug(e)


if config.config.get("start_date") and int(config.config.get("number_of_events")):
    start_date = config.config.get("start_date")
    end_date = datetime.datetime.utcnow()
    logging.info(
        "creating {} events between {} and {}".format(
            config.config["number_of_events"], start_date, end_date
        )
    )
    created_dates = get_created_dates(
        start_date, end_date, int(config.config["number_of_events"])
    )
    for created_date in created_dates:
        random_event(created_date=created_date)
else:
    for _ in range(int(config.config["number_of_events"])):
        random_event()

# generate site
site.gen_images()
site.gen_users_data()
site.gen_posts_data()

logging.info("stats: {}".format(site.get_stats()))
