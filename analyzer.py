import asyncio
import aio_pika
import json
import re
import emoji
from textblob import TextBlob

import configs


async def pre_processing(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    pa = re.compile(r"(.)\1{2,}")
    text = pa.sub(r"\1\1", text)
    text = text.replace('@', ' ').replace('#', ' ').replace('\t', ' ').replace('\n', ' ').replace('(', ' ').replace(')', ' ').replace(
        '/', ' ').replace(',', ' ').replace('.', ' ').replace(':', ' ').replace('!', ' ').replace('?', ' ').replace('|', ' ').replace('{', ' ').replace('}', ' ')
    text = re.sub("\\d+", '', text)
    text = emoji_pattern.sub(r' ', text)
    emojis = [c for c in text if c in emoji.UNICODE_EMOJI]
    for em in emojis:
        if em in text:
            text = text.replace(em, " ")
    text = text.strip()
    text = re.sub(' +', ' ', text)
    return text.strip()


async def publish_queue(message=None):
    await configs.RABBIT_CONNECTION.default_exchange.publish(aio_pika.Message(body=json.dumps(message, ensure_ascii=False).encode()), routing_key="datalayer")


async def analyze_sentiment(text):
    pre_processed_text = await pre_processing(text)
    analysis = TextBlob(pre_processed_text)
    return analysis.sentiment.polarity


async def analyze_subejectivity(text):
    pre_processed_text = await pre_processing(text)
    analysis = TextBlob(pre_processed_text)
    return analysis.sentiment.subjectivity


async def analyze(msg):
    save_msg = {
        "analysis": {
            "polarity": await analyze_sentiment(msg["text"]),
            "subjectivity": await analyze_subejectivity(msg["text"])
        }
    }
    req = {
        "type": "update",
        "collection": "posts",
        "condition": {"tweet_id": msg["tweet_id"]},
        "upsert": False,
        "body": save_msg
    }
    asyncio.create_task(publish_queue(req))


async def message_receiver(message: aio_pika.IncomingMessage):
    with message.process():
        msg = json.loads(message.body)
        if "text" in msg:
            asyncio.create_task(analyze(msg))


async def initialization(loop):
    try:
        print("Initializing Analayzer Service ...")
        connection = await aio_pika.connect_robust(
            url=f"amqp://{configs.RABBIT_USERNAME}:{configs.RABBIT_PASSWORD}@{configs.RABBIT_URL}:5672/%2F", loop=loop
        )
        configs.RABBIT_CONNECTION = await connection.channel()
        await configs.RABBIT_CONNECTION.set_qos(prefetch_count=1)

        analyzer_queue = await configs.RABBIT_CONNECTION.declare_queue("analyzer", durable=True, timeout=100)
        await analyzer_queue.consume(message_receiver)
    except Exception:
        print("There is a problem and we will try again in 15 seconds.")
        await asyncio.sleep(15)
        await initialization(loop)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(initialization(loop))
    loop.run_forever()
