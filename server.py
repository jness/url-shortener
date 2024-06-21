import string
import random
import logging

from flask import Flask, abort, request
from redis import Redis
from pymongo import MongoClient


logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

# connect to datastores
redis_client = Redis('redis')
mongo_client = MongoClient('mongo')

# use test mongo db and collection
db = mongo_client.test_database
collection = db.test_collection
urls = collection.urls


def randomize(size=6):
    """
    Create a random string of size
    """

    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=size))


def shorten_url(full_url):
    """
    Shorten a url to random string
    """

    # lookup url in mongo database
    result = get_mongo(full_url=full_url)

    if result:
        return result['short_url']

    # randomize a short string until not in database
    rand = randomize()
    while get_mongo(short_url=rand):
        rand = randomize()

    # save the result in database and cache
    set_mongo(full_url=full_url, short_url=rand)
    set_cache(short_url=rand, full_url=full_url)

    # return the random short string
    return rand
        

def get_cache(short_url):
    """
    Get value from cache
    """

    app.logger.debug(f'Looking for {short_url} in redis')
    return redis_client.get(short_url)


def set_cache(short_url, full_url):
    """
    Cache url
    """

    app.logger.debug(f'Saving {short_url} as {full_url} in redis')
    redis_client.set(short_url, full_url)


def get_mongo(**kwargs):
    """
    Get result from mongodb
    """

    app.logger.debug('Looking for %s in mongo' % kwargs)
    return urls.find_one(kwargs)


def set_mongo(full_url, short_url):
    """
    Set result to mongodb
    """

    app.logger.debug(f'Saving {full_url} as {short_url} in mongo')
    return urls.insert_one({'full_url': full_url, 'short_url': short_url})


def get_cache_or_database(short_url):
    """
    Get value from cache or fall back to database
    """

    # check for result in redis cache
    res = get_cache(short_url)
    if res:
        app.logger.debug(f'Found {short_url} in redis')
        return res
    
    # check for result in mongo database
    res = get_mongo(short_url=short_url)
    if res:
        # cache result from database
        app.logger.debug(f'Found {short_url} in mongo')
        set_cache(short_url=short_url, full_url=res['full_url'])
        return res['full_url']


@app.route("/url/shorten", methods=['POST'])
def url_shorten():
    """
    Shorten a url
    """

    data = request.get_json()

    if 'full_url' not in data:
        abort(500)

    short_url = shorten_url(data['full_url'])
    return short_url


@app.route("/r/<short_url>")
def url_resolve(short_url: str):
    """
    Resolve a short url
    """

    res = get_cache_or_database(short_url)
    if res:
        return res

    abort(404)


@app.route("/")
def index():
    return "Your URL Shortener is running!"

