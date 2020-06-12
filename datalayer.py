import asyncio
import aio_pika
import json
import motor.motor_asyncio

import configs


async def send_to_analyze(message):
    await configs.RABBIT_CONNECTION.default_exchange.publish(aio_pika.Message(body=json.dumps(message, ensure_ascii=False).encode()), routing_key="analyzer")

async def insert_query(req):
    await configs.MOTOR_CONNECTION[req["collection"]].insert_one(req["body"])

async def update_query(req):
    await configs.MOTOR_CONNECTION[req["collection"]].update_one(req["condition"], {"$set": req["body"]}, upsert=req.get("upsert", False))


async def database_message_receiver(message: aio_pika.IncomingMessage):
    with message.process():
        msg = json.loads(message.body)
        if msg["type"] == "update":
            asyncio.create_task(update_query(msg))
        if msg["type"] == "insert":
            asyncio.create_task(insert_query(msg))
        
        await send_to_analyze(msg["body"])


async def initialization(loop):
    try:
        print("Initializing Datalayer Service ...")
        connection = await aio_pika.connect_robust(
            url=f"amqp://{configs.RABBIT_USERNAME}:{configs.RABBIT_PASSWORD}@{configs.RABBIT_URL}:5672/%2F", loop=loop
        )
        configs.RABBIT_CONNECTION = await connection.channel()
        await configs.RABBIT_CONNECTION.set_qos(prefetch_count=1)

        datalayer_queue = await configs.RABBIT_CONNECTION.declare_queue("datalayer", durable=True, timeout=100)
        await configs.RABBIT_CONNECTION.declare_queue("analyzer", durable=True, timeout=100)

        dbClient = motor.motor_asyncio.AsyncIOMotorClient(
            f"mongodb://{configs.MONGODB_USERNAME}:{configs.MONGODB_PASSWORD}@{configs.MONGODB_URL}/?authSource=admin")
        configs.MOTOR_CONNECTION = dbClient[configs.MONGODB_DBNAME]

        await datalayer_queue.consume(database_message_receiver)
    except Exception:
        print("There is a problem and we will try again in 15 seconds.")
        await asyncio.sleep(15)
        await initialization(loop)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(initialization(loop))
    loop.run_forever()
