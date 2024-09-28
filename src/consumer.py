import logging
import asyncio

from typing import TYPE_CHECKING
from aio_pika import connect_robust, Message
from json.decoder import JSONDecodeError
from lxml.etree import XMLSyntaxError, XPathEvalError, ParseError

from src.config import settings

if TYPE_CHECKING:
    from typing import Callable
    from aio_pika import IncomingMessage


class RabbitMQConsumer:
    def __init__(self, queue_name: str, message_processor: "Callable"):
        self.max_retries = settings.MQ_MESSAGE_MAX_RETRIES_COUNT
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

    async def process_message(self, message: "IncomingMessage") -> None:
        try:
            await self.message_processor(message.body)
            await message.ack()
            logging.info(f"Message processed successfully: {message.message_id}")
        except JSONDecodeError as json_exception:
            logging.error(f"Invalid JSON in message body: {str(json_exception)}")
            await self._handle_retry(message)
        except ValueError as value_exception:
            logging.error(f"Invalid data format: {str(value_exception)}")
            await self._handle_retry(message)
        except XMLSyntaxError as xml_syntax_error:
            logging.error(f"XML Syntax Error: {str(xml_syntax_error)}")
            await self._handle_retry(message)
        except XPathEvalError as xpath_error:
            logging.error(f"XPath Evaluation Error: {str(xpath_error)}")
            await self._handle_retry(message)
        except ParseError as parse_error:
            logging.error(f"XML Parsing Error: {str(parse_error)}")
            await self._handle_retry(message)
        except AttributeError as attr_error:
            logging.error(
                f"Attribute Error (possibly missing XML element): {str(attr_error)}"
            )
            await self._handle_retry(message)
        except TypeError as type_error:
            logging.error(
                f"Type Error (possibly incorrect data type in XML operation): {str(type_error)}"
            )
            await self._handle_retry(message)
        except Exception as exception:
            logging.error(f"Error processing message: {exception}")
            await self._handle_retry(message)

    async def _handle_retry(self, message: "IncomingMessage") -> None:
        retry_count = int(message.headers.get("x-retry-count", 0))
        if retry_count < self.max_retries:
            await self._retry_message(message, retry_count)
        else:
            logging.warning(f"Max retries reached for message: {message.message_id}")
            await message.reject()

    async def _retry_message(
        self, message: "IncomingMessage", retry_count: int
    ) -> None:
        retry_count += 1
        await asyncio.sleep(2**retry_count)

        new_message = Message(body=message.body, headers={"x-retry-count": retry_count})

        await self.channel.default_exchange.publish(
            new_message, routing_key=self.queue_name
        )
        await message.ack()
        logging.info(
            f"Message requeued for retry {retry_count}/{self.max_retries}: {message.message_id}"
        )

    async def start_consuming(self) -> None:
        await self.queue.consume(self.process_message)
        logging.info("Started consuming messages. Press CTRL+C to exit.")

    async def run(self) -> None:
        await self.connect()
        await self.start_consuming()
        try:
            await asyncio.Future()
        finally:
            await self.connection.close()
