import asyncio
import logging
from typing import Dict
import random
import string

from src.publisher import RabbitMQPublisher
from src.config import settings


def generate_test_user_data() -> Dict[str, str]:
    return {
        "merchant_id": "78897722",
        # "sku": "123454343",
        "store_id": "PP6",
        # "store_name": "wonder_rest",
        # "offers": [
        #     {
        #         "sku": "123454343",
        #         "model": "title_233333333333333333333",
        #         "brand": "wonder_brand",
        #         "availabilities": [
        #             {"storeId": "PP5", "available": True},
        #             {"storeId": "PP6", "available": False},
        #         ],
        #         "cityprices": [{"cityId": "750000000", "price": 7261}],
        #         "price": 40000,
        #     },
        #     {
        #         "sku": "1234543489983",
        #         "model": "title_23333333333333",
        #         "brand": "wonder_brand",
        #         "availabilities": [
        #             {"storeId": "PP5", "available": True},
        #             {"storeId": "PP6", "available": False},
        #         ],
        #         "cityprices": [{"cityId": "750000000", "price": 7261}],
        #         "price": 40000,
        #     },
        # ],
    }


async def main():
    logging.basicConfig(level=logging.INFO)

    # publisher = RabbitMQPublisher(settings.MQ_CREATE_USER_XML_QUEUE)
    # publisher = RabbitMQPublisher(settings.MQ_ADD_NEW_OFFER_TO_XML_QUEUE)
    # publisher = RabbitMQPublisher(settings.MQ_DELETE_OFFER_XML_QUEUE)
    publisher = RabbitMQPublisher(settings.MQ_DISABLE_PICKUP_POINT_XML_QUEUE)

    try:
        for _ in range(1):
            test_data = generate_test_user_data()
            await publisher.publish_message(test_data)
            await asyncio.sleep(1)
    finally:
        await publisher.close()


if __name__ == "__main__":
    asyncio.run(main())
