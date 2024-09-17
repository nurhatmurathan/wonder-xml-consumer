import asyncio
from aio_pika import connect_robust, IncomingMessage


async def process_message(message: IncomingMessage):
    async with message.process():
        print(f"Received message: {message.body.decode()}")
        await asyncio.sleep(1)  # Simulating some work


async def main():
    connection = await connect_robust(
        "amqp://guest:guest@localhost/"
    )

    # Creating a channel
    channel = await connection.channel()

    # Declaring a queue
    queue = await channel.declare_queue("my_queue", durable=True)

    # Start consuming messages
    await queue.consume(process_message)

    print("Waiting for messages. To exit press CTRL+C")
    try:
        await asyncio.Future()  # Run forever
    finally:
        await connection.close()

if __name__ == "__main__":
    asyncio.run(main())