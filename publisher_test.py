import asyncio
import logging
from typing import Dict
import random
import string

from src.publisher import RabbitMQPublisher
from src.config import settings


def test_MQ_CREATE_USER_XML_QUEUE() -> Dict[str, str]:
    return {"merchant_id": "58585777", "store_name": "Wonder"}


def test_MQ_ADD_NEW_OFFER_TO_XML_QUEUE() -> Dict[str, str]:
    return {
        "merchant_id": "58585777",
        "offers": [
            {
                "sku": "1",
                "model": "TITLE_WEBS",
                "brand": "WonderIder12121",
                "availabilities": [
                    {"store_id": "PP1", "available": True},
                    {"store_id": "PP2", "available": True},
                ],
                # "city_prices": [{"city_id": "750000000", "price": 7261}],
                "price": 8285,
            },
            {
                "sku": "2",
                "model": "TITLE_WEBS_WEWEWEWE",
                "brand": "WonderIDDEDEE",
                "availabilities": [
                    {"store_id": "PP12", "available": True},
                    {"store_id": "PP32", "available": True},
                ],
                "city_prices": [{"city_id": "750000000", "price": 7261}],
                # "price": 7500,
            },
        ],
    }


def test_MQ_DELETE_OFFER_XML_QUEUE() -> Dict[str, str]:
    return {"merchant_id": "58585777", "sku": "111"}


def test_MQ_DISABLE_PICKUP_POINT_XML_QUEUE() -> Dict[str, str]:
    return {"merchant_id": "58585777", "store_id": "PP12"}


def test_MQ_ENABLE_PICKUP_POINT_XML_QUEUE() -> Dict[str, str]:
    return {
        "merchant_id": "58585777",
        "store_id": "PP1",
        "offers_sku": ["1", "2"],
    }


def test_MQ_SET_CITY_PRICES_XML_QUEUE() -> Dict[str, str]:
    return {
        "merchant_id": "58585777",
        "offer": {
            "sku": "1",
            "city_prices": [
                {"city_id": "750000000", "price": 7261},
                {"city_id": "710000000", "price": 7750},
                {"city_id": "7100000033430", "price": 7750},
            ],
            "price": 7500,
        },
    }


def test_MQ_SET_STORE_AVAILABILITY_XML_QUEUE() -> Dict[str, str]:
    return {
        "merchant_id": "58585777",
        "sku": "1",
        "store_id": "PP1",
        "available": True,
    }


async def main():
    logging.basicConfig(level=logging.INFO)

    publisher = RabbitMQPublisher(settings.MQ_CREATE_USER_XML_QUEUE)
    publisher = RabbitMQPublisher(settings.MQ_ADD_NEW_OFFER_TO_XML_QUEUE)
    publisher = RabbitMQPublisher(settings.MQ_DELETE_OFFER_XML_QUEUE)
    publisher = RabbitMQPublisher(settings.MQ_DISABLE_PICKUP_POINT_XML_QUEUE)
    publisher = RabbitMQPublisher(settings.MQ_ENABLE_PICKUP_POINT_XML_QUEUE)
    publisher = RabbitMQPublisher(settings.MQ_SET_CITY_PRICES_XML_QUEUE)
    publisher = RabbitMQPublisher(settings.MQ_SET_STORE_AVAILABILITY_XML_QUEUE)

    try:
        for _ in range(1):
            test_data = test_MQ_SET_STORE_AVAILABILITY_XML_QUEUE()
            await publisher.publish_message(test_data)
            await asyncio.sleep(1)
    finally:
        await publisher.close()


if __name__ == "__main__":
    asyncio.run(main())
