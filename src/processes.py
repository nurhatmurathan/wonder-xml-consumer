import logging
from typing import TYPE_CHECKING


from src.services import XMLService, GCPUploadService
from src.schemas import (
    CreateUserSchema,
    AddNewOffersSchema,
    DeleteOfferSchema,
    DisablePickupSchema,
)
from src.exceptions_handler import process_exception_handler
from src.config import settings

if TYPE_CHECKING:
    from aio_pika import IncomingMessage
    from typing import Callable, Any
    from lxml.etree import Element


class XMLProcessor:
    def __init__(self):
        self.xml_service = XMLService()
        self.gcp_service = GCPUploadService()

    async def process_xml_message(
        self,
        message: "IncomingMessage",
        schema_class: "Any",
        xml_operation: Callable[["Element", "Any"], "Element"],
    ) -> None:
        async with message.process():
            logging.info(f"Processing START")

            payload = message.body.decode()
            logging.info(f"Step 1 | Processing import: {payload}")

            data = schema_class.model_validate_json(payload)
            logging.info(f"Step 2 | Pydantic model converted from payload: {data}")

            destination = f"{settings.TEST_GCP_STORAGE_DESTINATION}/{data.merchant_id}/products.xml"

            xml_string_content = self.gcp_service.download_xml(destination)
            logging.info(f"Step 3 | Content of String XML: {xml_string_content}")
            root = self.xml_service.string_to_xml(xml_string_content)

            updated_root = xml_operation(root, data)
            updated_xml_content = self.xml_service.xml_to_string(updated_root)
            logging.info(f"Step 4 | Updated XML content: {updated_xml_content}")

            url = self.gcp_service.upload_xml(updated_xml_content, destination)
            logging.info(f"Step 5 | Updated XML uploaded to: {url}")

    @process_exception_handler
    async def process_create_user_xml_message(self, message: "IncomingMessage"):
        async with message.process():
            logging.info("In create user XML message processes")

            payload = message.body.decode()
            logging.info(f"Step 1 | Processing import: {payload}")

            data = CreateUserSchema.model_validate_json(payload)
            logging.info(f"Step 2 | Pydantic model converted from payload: {data}")

            xml_service = self.xml_service
            root = xml_service.create_user_xml(data)
            logging.info(f"Step 3 | Root of created xml: {root}")

            xml_content = XMLService.xml_to_string(root)
            logging.info(f"Step 4 | Content of XML: {xml_content}")

            gcp_service = self.gcp_service
            destination = f"{settings.TEST_GCP_STORAGE_DESTINATION}/{data.merchant_id}/products.xml"
            url = gcp_service.upload_xml(xml_content, destination)

            logging.info(f"XML uploaded successfully. URL: {url}")

    @process_exception_handler
    async def process_add_new_offers_to_xml_message(self, message: "IncomingMessage"):
        await self.process_xml_message(
            message,
            AddNewOffersSchema,
            self.xml_service.add_offers_to_xml,
        )

    @process_exception_handler
    async def process_delete_offers_from_xml_message(self, message: "IncomingMessage"):
        await self.process_xml_message(
            message,
            DeleteOfferSchema,
            self.xml_service.delete_offer_from_xml,
        )

    @process_exception_handler
    async def process_disable_pickup_point_xml_message(
        self, message: "IncomingMessage"
    ):
        await self.process_xml_message(
            message,
            DisablePickupSchema,
            self.xml_service.disable_pickup_point,
        )
