import logging
import time
from typing import TYPE_CHECKING, Optional, List
from lxml.etree import fromstring, XMLParser, tostring, Element

if TYPE_CHECKING:
    from src.schemas import (
        CreateUserSchema,
        AddNewOffersSchema,
        OfferAvailabilitySchema,
        OfferCityPriceSchema,
        DeleteOfferSchema,
        DisablePickupSchema,
        EnablePickupSchema,
        SetOfferPriceSchema,
        OfferPriceSchema,
        SetStoreAvailabilitySchema,
        AddStoresToOfferSchema,
    )


class XMLService:
    NAMESPACE = "kaspiShopping"
    NAMESPACE_XSI = "http://www.w3.org/2001/XMLSchema-instance"
    XSI_SCHEMA_LOCATION = "http://kaspi.kz/kaspishopping.xsd"
    NS = {"ns": NAMESPACE}
    NSMAP = {
        None: NAMESPACE,
        "xsi": NAMESPACE_XSI,
    }

    def _create_element(
        self, tag: str, parent: Optional["Element"] = None, **attrs
    ) -> "Element":
        element = Element(f"{{{XMLService.NAMESPACE}}}{tag}", nsmap=self.NSMAP, **attrs)

        if parent is not None:
            parent.append(element)

        return element

    def _get_or_create_offer_elem(self, root: "Element", sku: str):
        offer_elem = root.find(f".//ns:offer[@sku='{sku}']", namespaces=self.NS)

        if offer_elem is None:
            offers_elem = root.find("ns:offers", namespaces=self.NS)
            offer_elem = self._create_element("offer", offers_elem, sku=sku)
            self._create_element("availabilities", offer_elem)

        return offer_elem

    def _get_or_create_availability_elem(
        self, availabilities_elem: "Element", store_id: str, available: str
    ):
        availability_elem = availabilities_elem.find(
            f"ns:availability[@storeId='{store_id}']", namespaces=self.NS
        )

        if availability_elem is None:
            availability_elem = self._create_element(
                "availability",
                availabilities_elem,
                storeId=store_id,
                available=available,
            )

        return availability_elem

    def create_user_xml(self, data: "CreateUserSchema") -> "Element":
        root = self._create_element("kaspi_catalog")
        root.set(
            f"{{{self.NAMESPACE_XSI}}}schemaLocation",
            f"{self.NAMESPACE} {self.XSI_SCHEMA_LOCATION}",
        )
        root.set("date", str(int(time.time())))

        self._create_element("company", root).text = data.store_name
        self._create_element("merchantid", root).text = data.merchant_id
        self._create_element("offers", root)

        return root

    def add_offers_to_xml(
        self, root: "Element", data: "AddNewOffersSchema"
    ) -> "Element":
        offers_elem = root.find("ns:offers", namespaces=self.NS)

        for offer_data in data.offers:
            if (
                root.find(f".//ns:offer[@sku='{offer_data.sku}']", namespaces=self.NS)
                is not None
            ):
                logging.warning(f"Offer with {offer_data.sku} already exists")
                continue

            offer_elem = self._create_element("offer", offers_elem, sku=offer_data.sku)
            self._create_element("model", offer_elem).text = offer_data.model

            if offer_data.brand:
                self._create_element("brand", offer_elem).text = offer_data.brand

            self._add_availabilities(offer_elem, offer_data.availabilities)

            if offer_data.price:
                self._create_element("price", offer_elem).text = str(offer_data.price)
            elif offer_data.city_prices:
                self._add_city_prices(offer_elem, offer_data.city_prices)

        return root

    def _add_availabilities(
        self, offer_elem: "Element", data: List["OfferAvailabilitySchema"]
    ):
        availabilities_elem = self._create_element("availabilities", offer_elem)
        for availability_data in data:
            if availability_data.available:
                self._get_or_create_availability_elem(
                    availabilities_elem,
                    availability_data.store_id,
                    available="yes",
                )

    def _add_city_prices(
        self, offer_elem: "Element", data: List["OfferCityPriceSchema"]
    ):
        city_prices_elem = self._create_element("cityprices", offer_elem)
        for city_price_data in data:
            price_elem = self._create_element(
                "cityprice", city_prices_elem, cityId=city_price_data.city_id
            )
            price_elem.text = str(city_price_data.price)

    def delete_offer_from_xml(
        self, root: "Element", data: "DeleteOfferSchema"
    ) -> "Element":
        offers_elem_to_remove = root.find(
            f".//ns:offer[@sku='{data.sku}']", namespaces=self.NS
        )

        if offers_elem_to_remove is None:
            logging.warning(f"No offers found with SKU {data.sku}")
            return root

        parent = offers_elem_to_remove.getparent()
        parent.remove(offers_elem_to_remove)
        return root

    def disable_pickup_point_xml(
        self, root: "Element", data: "DisablePickupSchema"
    ) -> "Element":
        availabilities_elem = root.findall(
            f".//ns:availability[@storeId='{data.store_id}']", namespaces=self.NS
        )
        for availability_elem in availabilities_elem:
            parent = availability_elem.getparent()
            parent.remove(availability_elem)

        return root

    def enable_pickup_point_xml(
        self, root: "Element", data: "EnablePickupSchema"
    ) -> "Element":
        for sku in data.offers_sku:
            offer_elem = self._get_or_create_offer_elem(root, sku=sku)

            availabilities_elem = offer_elem.find(
                "ns:availabilities", namespaces=self.NS
            )
            self._get_or_create_availability_elem(
                availabilities_elem, data.store_id, "yes"
            )

        return root

    def set_city_prices_xml(self, root: "Element", data: "SetOfferPriceSchema"):
        offer_elem = self._get_or_create_offer_elem(root, sku=data.offer.sku)

        if data.offer.price:
            self._handle_price_existence_logic_in_set_city_prices_xml(
                offer_elem, data.offer
            )
        elif data.offer.city_prices:
            self._handle_city_price_existence_logic_in_set_city_prices_xml(
                offer_elem, data.offer
            )

        return root

    def _handle_price_existence_logic_in_set_city_prices_xml(
        self, offer_elem: "Element", data: "OfferPriceSchema"
    ):
        city_prices_elem = offer_elem.find("ns:cityprices", namespaces=self.NS)
        if city_prices_elem is not None:
            offer_elem.remove(city_prices_elem)

        price_elem = offer_elem.find("ns:price", namespaces=self.NS)
        if price_elem is not None:
            price_elem.text = str(data.price)
        else:
            price_elem = self._create_element("price", offer_elem).text = str(
                data.price
            )

        return price_elem

    def _handle_city_price_existence_logic_in_set_city_prices_xml(
        self, offer_elem: "Element", data: "OfferPriceSchema"
    ):
        price_elem = offer_elem.find("ns:price", namespaces=self.NS)
        if price_elem is not None:
            offer_elem.remove(price_elem)

        city_prices_elem = offer_elem.find("ns:cityprices", namespaces=self.NS)
        if city_prices_elem is not None:
            offer_elem.remove(city_prices_elem)

        self._add_city_prices(offer_elem, data.city_prices)

    def set_store_availability_xml(
        self, root: "Element", data: "SetStoreAvailabilitySchema"
    ):
        offer_elem = self._get_or_create_offer_elem(root, sku=data.sku)
        availabilities_elem = offer_elem.find("ns:availabilities", namespaces=self.NS)

        availability_elem = self._get_or_create_availability_elem(
            availabilities_elem, data.store_id, available="yes"
        )
        if not data.available:
            availabilities_elem.remove(availability_elem)

        return root

    def add_stores_to_offer_xml(self, root: "Element", data: "AddStoresToOfferSchema"):
        offer_elem = self._get_or_create_offer_elem(root, sku=data.sku)
        availabilities_elem = offer_elem.find("ns:availabilities", namespaces=self.NS)

        for availability_data in data.availabilities:
            availability_elem = self._get_or_create_availability_elem(
                availabilities_elem, availability_data.store_id, available="yes"
            )

            if not availability_data.available:
                availabilities_elem.remove(availability_elem)

        return root

    @staticmethod
    def xml_to_string(root: "Element") -> str:
        return tostring(root, encoding="UTF-8", pretty_print=True, xml_declaration=True)

    @staticmethod
    def string_to_xml(xml_string: str) -> "Element":
        parser = XMLParser(remove_blank_text=True, remove_comments=False)
        return fromstring(xml_string.encode(), parser=parser)
