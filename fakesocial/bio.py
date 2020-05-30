"""
"""

import csv
import logging
import random

import markovify
import names


world_cities_file = "data/world-cities_csv.csv"
job_titles_file = "data/job-titles.txt"
nasdaq_listings_file = "data/nasdaq-listed_csv.csv"

job_titles_model = None


def _gen_full_name_v2():
    """Real name with one letter swapped in both first and last names."""
    first_name = names.get_first_name()
    last_name = names.get_last_name()

    f1 = random.choice([_modify_consonants, _modify_vowels])
    f2 = random.choice([_modify_consonants, _modify_vowels])

    return "{} {}".format(f1(first_name, count=1), f2(last_name, count=1))


def _gen_full_name_v1():
    """Made up pronounceable name."""

    def _gen_name():
        c = "bcdfghjklmnpqrstvwxz"
        v = "aeiouy"
        order = [c, v]
        length = random.randint(2, 8)

        groups = []
        for i in range(length):
            groups.append(order[i % 2])

        return "".join(map(random.choice, groups)).capitalize()

    full_name = "{} {}".format(_gen_name(), _gen_name())
    logging.debug("{} -> generated new name".format(full_name))
    return full_name


def gen_full_name():
    return _gen_full_name_v2()


def _get_random_city():
    line = None
    with open(world_cities_file) as f:
        lines = f.readlines()
        line = lines[random.randint(1, len(lines) - 1)]
    comp = line.split(",")
    logging.debug("{} -> returning city from list".format(comp[0]))
    return "{}, {}, {}".format(comp[0], comp[2], comp[1])


def get_random_job_title():
    line = None

    with open(job_titles_file) as f:
        lines = f.readlines()
        line = lines[random.randint(0, len(lines) - 1)]

    job_title = " ".join([l.capitalize() for l in line.split()])
    logging.debug("{} -> returning job title from list".format(job_title))
    return job_title


def gen_job_title():
    line = None

    global job_titles_model
    if not job_titles_model:
        with open(job_titles_file) as f:
            job_titles_model = markovify.NewlineText(
                f.read(), well_formed=False
            ).compile()
    line = job_titles_model.make_short_sentence(50, tries=1000)

    job_title = " ".join([l.capitalize() for l in line.split()])
    logging.debug("{} -> generating job title using list".format(job_title))
    return job_title


def _get_random_company_name():
    with open(nasdaq_listings_file) as f:
        company_list = list(csv.reader(f))[1:]
        company_name = random.choice(company_list)[1]
        return company_name


def _swap_letters(word, letters, count):
    c = set(letters)
    word = list(word.lower())
    count = count or len(word)
    for i in range(len(word)):
        if word[i] in c:
            word[i] = random.choice(list(c.difference(word[i])))
            count -= 1
            if count == 0:
                break
    return "".join(word).capitalize()


def _modify_consonants(word, count=None):
    return _swap_letters(word, "bcdfghjklmnpqrstvwxz", count)


def _modify_vowels(word, count=None):
    return _swap_letters(word, "aeiouy", count)


def gen_company_name():
    result = []
    for name in _get_random_company_name().split():
        func = random.choice([_modify_consonants, _modify_vowels])
        result.append(func(name, 1))
    return " ".join(result)


def gen_location():
    result = []
    for name in _get_random_city().split():
        func = random.choice([_modify_consonants, _modify_vowels])
        result.append(func(name, 1))
    return " ".join(result)
