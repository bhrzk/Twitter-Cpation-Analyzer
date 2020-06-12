import asyncio
import aio_pika
import tweepy
import random
import json

import configs

twitter_auth = tweepy.OAuthHandler(
    configs.TWITTER_API_KEY, configs.TWITTER_API_SECRET)
twitter_auth.set_access_token(
    configs.TWITTER_ACCESS_TOKEN, configs.TWITTER_TOKEN_SECRET)
twitter_api = tweepy.API(twitter_auth)


async def publish_queue(message=None):
    await configs.RABBIT_CONNECTION.default_exchange.publish(aio_pika.Message(body=json.dumps(message, ensure_ascii=False).encode()), routing_key="datalayer")


async def get_user_timeline(user):
    print("get_user_timeline CALLED ->", user["id"])
    saving_user_message = {
        "type": "update",
        "collection": "users",
        "condition": {"id": user["id"]},
        "upsert": True,
        "body": user
    }
    asyncio.create_task(publish_queue(saving_user_message))
    await asyncio.sleep(random.randint(3, 10))

    timeline=twitter_api.user_timeline(user_id=int(user["id"]))
    async_queues=[
        asyncio.create_task(
            publish_queue(
                {
                    "type": "insert",
                    "collection": "posts",
                    "body": {
                        "tweet_id": status._json["id_str"],
                        "text": status._json["text"],
                        "user_id": status._json["user"]["id_str"],
                        "entities": status._json["entities"]
                    }
                }
            )
        )
        for status in timeline
    ]


async def get_tweets():
    tweets=twitter_api.search(
        q=configs.SEED_KEYWORDS, result_type="recent", count=5, lang="en")

    async_queues=[
        asyncio.create_task(
            get_user_timeline({
                "id": tweet._json["user"]["id_str"],
                "name": tweet._json["user"]["name"],
                "screen_name": tweet._json["user"]["screen_name"],
                "location": tweet._json["user"]["location"],
                "description": tweet._json["user"]["description"],
                "followers_count": tweet._json["user"]["followers_count"],
                "friends_count": tweet._json["user"]["friends_count"],
                "listed_count": tweet._json["user"]["listed_count"],
                "created_at": tweet._json["user"]["created_at"],
                "favourites_count": tweet._json["user"]["favourites_count"],
                "statuses_count": tweet._json["user"]["statuses_count"],
                "favourites_count": tweet._json["user"]["favourites_count"],
            })
        )
        for tweet in tweets
    ]


async def initialization(loop):
    await asyncio.sleep(20)
    try:
        print("Initializing Crawler Service ...")
        connection=await aio_pika.connect_robust(
            url=f"amqp://{configs.RABBIT_USERNAME}:{configs.RABBIT_PASSWORD}@{configs.RABBIT_URL}:5672/%2F", loop=loop
        )
        configs.RABBIT_CONNECTION=await connection.channel()

        await configs.RABBIT_CONNECTION.declare_queue("datalayer", durable=True, timeout=100)

        await get_tweets()
    except Exception:
        print("There is a problem and we will try again in 15 seconds.")
        await asyncio.sleep(15)
        await initialization(loop)


if __name__ == "__main__":
    loop=asyncio.get_event_loop()
    loop.run_until_complete(initialization(loop))
    loop.run_forever()
