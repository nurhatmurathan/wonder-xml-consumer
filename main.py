import asyncio
import logging
from typing import Callable, Dict, TYPE_CHECKING, Coroutine

from aio_pika import IncomingMessage

from src.processes import XMLMessageProcessor
from src.config import settings
from src.consumer import RabbitMQConsumer

if TYPE_CHECKING:
    ProcessFunc = Callable[[IncomingMessage], Coroutine[None, None, None]]


async def run_consumer(queue_name: str, process_func: "ProcessFunc") -> None:
    consumer = RabbitMQConsumer(queue_name, process_func)
    await consumer.run()


async def main() -> None:
    settings.configure_logging(level=logging.INFO)

    xml_processor = XMLMessageProcessor()
    queue_process_map: Dict[str, "ProcessFunc"] = {
        settings.MQ_CREATE_USER_XML_QUEUE: xml_processor.process_create_user_xml_message,
        settings.MQ_ADD_NEW_OFFER_TO_XML_QUEUE: xml_processor.process_add_new_offers_to_xml_message,
        settings.MQ_DELETE_OFFER_XML_QUEUE: xml_processor.process_delete_offers_from_xml_message,
        settings.MQ_DISABLE_PICKUP_POINT_XML_QUEUE: xml_processor.process_disable_pickup_point_xml_message,
        settings.MQ_ENABLE_PICKUP_POINT_XML_QUEUE: xml_processor.process_enable_pickup_point_xml_message,
        settings.MQ_SET_CITY_PRICES_XML_QUEUE: xml_processor.process_set_city_prices_xml_message,
        settings.MQ_SET_STORE_AVAILABILITY_XML_QUEUE: xml_processor.process_set_store_availability_xml_message,
        settings.MQ_ADD_STORES_TO_OFFER_XML_QUEUE:  xml_processor.process_add_stores_to_offer_xml_message
    }

    consumer_tasks = [
        asyncio.create_task(run_consumer(queue_name, process_func))
        for queue_name, process_func in queue_process_map.items()
    ]
    await asyncio.gather(*consumer_tasks)


if __name__ == "__main__":
    asyncio.run(main())
