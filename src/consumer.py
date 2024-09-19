import logging
import asyncio

from aio_pika import connect_robust
from typing import TYPE_CHECKING


from src.config import settings

if TYPE_CHECKING:
    from typing import Callable


class RabbitMQConsumer:
    def __init__(self, queue_name: str, message_processor: "Callable"):
        self.queue_name = queue_name
        self.message_processor = message_processor
        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self) -> None:
        self.connection = await connect_robust(settings.rmq_url)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name, durable=True)
        logging.info(f"Queue: {self.queue_name} DECLARE")

    async def start_consuming(self) -> None:
        await self.queue.consume(self.message_processor)
        logging.info("Started consuming messages. Press CTRL+C to exit.")

    async def run(self) -> None:
        await self.connect()
        await self.start_consuming()
        try:
            await asyncio.Future()
        finally:
            await self.connection.close()
