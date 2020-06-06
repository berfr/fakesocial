# fakesocial

Fake social network using generated content.

See https://berfr.github.io/posts/fakesocial for more info.

## Setup

```shell
# Setup virtual environment and install dependencies
python -m venv venv && . venv/bin/activate
pip install -r requirements.txt

# Generated site located under `site/` directory by default
python -m fakesocial
python -m http.server -d site
open http://localhost:8000/
```

## Content sources

- Job titles: https://github.com/jneidel/job-titles
- Names: https://github.com/treyhunner/names
- Nasdaq listings: https://datahub.io/core/nasdaq-listings
- Profile pictures: https://thispersondoesnotexist.com
- Quotes: https://www.kaggle.com/coolcoder22/quotes-dataset
- World cities: https://datahub.io/core/world-cities

## Content generators

- Markovify: https://github.com/jsvine/markovify
- random module: https://docs.python.org/3/library/random.html

## Configuration

These options can be set in a JSON file and specified with the `--config-file FILENAME` argument or can be passed using the `--config key1=value1 key2=value2` argument.

key name | description
--- | ---
`db_file` | Specify which database file to use. This is useful to save current state. If file contains data, `fakesocial` will continue where is left off.
`number_of_events` | The total number of events to create.
`output_dir` | Which directory to place generated website.
`start_date` | The date where events start off. Ex: 2010-01-25.
