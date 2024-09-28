import logging
from typing import TYPE_CHECKING, Callable

from src.services import XMLService, GCPUploadService
from src.config import settings
from src.schemas import (
    CreateUserSchema,
    AddNewOffersSchema,
    DeleteOfferSchema,
    DisablePickupSchema,
    EnablePickupSchema,
    SetOfferPriceSchema,
    SetStoreAvailabilitySchema,
    AddStoresToOfferSchema,
)

if TYPE_CHECKING:
    from typing import Any
    from lxml.etree import Element


class XMLMessageProcessor:
    def __init__(self):
        self.xml_service = XMLService()
        self.gcp_service = GCPUploadService()
        self.file_path = settings.GCP_STORAGE_XML_FILE_PATH

    async def process_xml_message(
        self,
        body: bytes,
        schema_class: "Any",
        xml_operation: Callable[["Element", "Any"], "Element"],
    ) -> None:
        logging.info(f"Processing START {xml_operation}")

        payload = body.decode()
        logging.info(f"Step 1 | Processing import")

        data = schema_class.model_validate_json(payload)
        logging.info(f"Step 2 | Pydantic model converted from payload:")

        destination = f"{self.file_path}/{data.merchant_id}/products.xml"
        xml_string_content = self.gcp_service.download_xml(destination)
        logging.info(f"Step 3 | Content of String XML")

        root = XMLService.string_to_xml(xml_string_content)

        updated_root = xml_operation(root, data)
        updated_xml_string_content = XMLService.xml_to_string(updated_root)
        logging.info(f"Step 4 | Updated XML content")

        url = self.gcp_service.upload_xml(updated_xml_string_content, destination)
        logging.info(f"Step 5 | Updated XML uploaded to: {url}")

    async def process_create_user_xml_message(self, body: bytes):
        logging.info("In create user XML message processes")

        payload = body.decode()
        logging.info(f"Step 1 | Processing import")

        data = CreateUserSchema.model_validate_json(payload)
        logging.info(f"Step 2 | Pydantic model converted from payload")

        root = self.xml_service.create_user_xml(data)
        logging.info(f"Step 3 | Root of created xml")

        xml_content = XMLService.xml_to_string(root)
        logging.info(f"Step 4 | Content of XML")

        destination = f"{self.file_path}/{data.merchant_id}/products.xml"
        url = self.gcp_service.upload_xml(xml_content, destination)
        logging.info(f"Step 5 | XML uploaded successfully. URL: {url}")

    async def process_add_new_offers_to_xml_message(self, body: bytes):
        await self.process_xml_message(
            body,
            AddNewOffersSchema,
            self.xml_service.add_offers_to_xml,
        )

    async def process_delete_offers_from_xml_message(self, body: bytes):
        await self.process_xml_message(
            body,
            DeleteOfferSchema,
            self.xml_service.delete_offer_from_xml,
        )

    async def process_disable_pickup_point_xml_message(self, body: bytes):
        await self.process_xml_message(
            body,
            DisablePickupSchema,
            self.xml_service.disable_pickup_point_xml,
        )

    async def process_enable_pickup_point_xml_message(self, body: bytes):
        await self.process_xml_message(
            body, EnablePickupSchema, self.xml_service.enable_pickup_point_xml
        )

    async def process_set_city_prices_xml_message(self, body: bytes):
        await self.process_xml_message(
            body, SetOfferPriceSchema, self.xml_service.set_city_prices_xml
        )

    async def process_set_store_availability_xml_message(self, body: bytes):
        await self.process_xml_message(
            body,
            SetStoreAvailabilitySchema,
            self.xml_service.set_store_availability_xml,
        )

    async def process_add_stores_to_offer_xml_message(self, body: bytes):
        await self.process_xml_message(
            body, AddStoresToOfferSchema, self.xml_service.add_stores_to_offer_xml
        )
