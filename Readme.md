# Simple Twitter Analyzer 

## Description

This python module gets tweets based on keywords from twitter and does some basic analyzes on them.
This microservice was part of a bigger project and used as a helper to the main module.


## Process

This module follows three steps:
1- Getting a certain amount of tweets based on pre-defined keywords.
2- Getting one page of the latest tweets of users. (timeline)
3- Run analyzes
4- Save in the database

## Technologies

1- Twitter API (tweepy)
3- AsyncIO
4- RabbitMQ
5- MongoDB

## Configs

Please be careful to take a look at the `config.py` file before starting. There are a few things you need to pay attention to. 

```python

    # Twitter API access configuration

    TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")
    TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
    TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
    TWITTER_TOKEN_SECRET = os.environ.get("TWITTER_TOKEN_SECRET", "")

    
    # RabbitMQ Configuration
    # You can leave it alone but be noticed you need to set the same value to docker-compose.yml as well.
    
    RABBIT_USERNAME = os.environ.get("RABBIT_USERNAME", "admin")
    RABBIT_PASSWORD = os.environ.get("RABBIT_PASSWORD", "123123")
    RABBIT_URL = os.environ.get("RABBIT_URL", "localhost")

    # MongoDB Configuration
    # You can leave it alone but be noticed you need to set the same value to docker-compose.yml as well.

    MONGODB_USERNAME = os.environ.get("MONGODB_USERNAME", "dbuser")
    MONGODB_PASSWORD = os.environ.get("MONGODB_PASSWORD", "dbpassword")
    MONGODB_URL = os.environ.get("MONGODB_URL", "localhost:27017")
    MONGODB_DBNAME = os.environ.get("MONGODB_DBNAME", "tw_analyzer")

    # These are the keywords that the module will look for on Twitter at starting. It's for the best to not exceed 10 items. 

    SEED_KEYWORDS = ["puma", "adidas", "zara"]

```

## Analysis

The concept of this helper microservice is to run two analysis: 

**1- Polarity**
Polarity will show the positive and negative rate of a text. There return if a numeric float between -1 to 1. The lower shows more negative and the higher show positive. 0.0 also shows natural.

**2- Subjectivity**
It's a float between 0.0 to 1.0 that shows the subjectivity or objectivity of a content. The 0.0 shows the content is very objective and 1.0 is very subjective.


## Run

```shell
    docker-compose up --build
```

## Stopping and Cleanup

```shell
    docker-compose down
```