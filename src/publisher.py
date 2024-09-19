import json
import logging
from typing import Dict, Any

from aio_pika import connect_robust, Message

from src.config import settings


class RabbitMQPublisher:
    def __init__(self, queue_name: str):
        self.connection = None
        self.channel = None
        self.queue_name = queue_name

    async def connect(self) -> None:
        self.connection = await connect_robust(settings.rmq_url)
        self.channel = await self.connection.channel()
        logging.info("Connected to RabbitMQ")

    async def publish_message(self, message: Dict[str, Any]) -> None:
        if not self.channel:
            await self.connect()

        json_message = json.dumps(message)
        await self.channel.default_exchange.publish(
            Message(body=json_message.encode()), routing_key=self.queue_name
        )
        logging.info(f"Published message: {message}")

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()
            logging.info("Closed RabbitMQ connection")
