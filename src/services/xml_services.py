import logging
import time
from typing import TYPE_CHECKING, List, Optional
from lxml.etree import (
    Element,
    fromstring,
    XMLParser,
    tostring,
)

if TYPE_CHECKING:
    from src.schemas import (
        CreateUserSchema,
        AddNewOffersSchema,
        OfferAvailabilitySchema,
        OfferCityPriceSchema,
        DeleteOfferSchema,
        DisablePickupSchema,
    )


class XMLService:
    NAMESPACE = "kaspiShopping"
    NAMESPACE_XSI = "http://www.w3.org/2001/XMLSchema-instance"
    XSI_SCHEMA_LOCATION = "http://kaspi.kz/kaspishopping.xsd"
    ns = {"ns": NAMESPACE}
    NSMAP = {
        None: NAMESPACE,
        "xsi": NAMESPACE_XSI,
    }

    @staticmethod
    def create_element(tag: str, parent: Optional[Element] = None, **attrs) -> Element:
        element = Element(
            f"{{{XMLService.NAMESPACE}}}{tag}", nsmap=XMLService.NSMAP, **attrs
        )

        if parent is not None:
            parent.append(element)

        return element

    def create_user_xml(self, data: "CreateUserSchema") -> Element:
        root = self.create_element("kaspi_catalog")
        root.set(
            f"{{{self.NAMESPACE_XSI}}}schemaLocation",
            f"{self.NAMESPACE} {self.XSI_SCHEMA_LOCATION}",
        )
        root.set("date", str(int(time.time())))

        self.create_element("company", root).text = data.store_name
        self.create_element("merchantid", root).text = data.merchant_id
        self.create_element("offers", root)

        return root

    def add_offers_to_xml(self, root: Element, data: "AddNewOffersSchema") -> Element:
        offers_elem = root.find("ns:offers", namespaces=self.ns)
        if offers_elem is None:
            offers_elem = self.create_element("offers", root)

        for offer in data.offers:
            offer_elem = self.create_element("offer", offers_elem, sku=offer.sku)
            self.create_element("model", offer_elem).text = offer.model

            if offer.brand:
                self.create_element("brand", offer_elem).text = offer.brand

            self._add_availabilities(offer_elem, offer.availabilities)

            if offer.price:
                self.create_element("price", offer_elem).text = str(offer.price)
            elif offer.city_prices:
                self._add_city_prices(offer_elem, offer.city_prices)

        return root

    def _add_availabilities(
        self, offer_elem: Element, availabilities: List["OfferAvailabilitySchema"]
    ):
        availabilities_elem = self.create_element("availabilities", offer_elem)
        for availability in availabilities:
            self.create_element(
                "availability",
                availabilities_elem,
                storeId=availability.storeId,
                available="yes" if availability.available else "no",
            )

    def _add_city_prices(
        self, offer_elem: Element, city_prices: List["OfferCityPriceSchema"]
    ):
        city_prices_elem = self.create_element("cityprices", offer_elem)
        for city_price in city_prices:
            price_elem = self.create_element(
                "cityprice", city_prices_elem, cityId=city_price.cityId
            )
            price_elem.text = str(city_price.price)

    def delete_offer_from_xml(
        self, root: Element, data: "DeleteOfferSchema"
    ) -> Element:
        offers_to_remove = root.find(
            f".//ns:offer[@sku='{data.sku}']", namespaces=self.ns
        )

        if offers_to_remove:
            parent = offers_to_remove.getparent()
            parent.remove(offers_to_remove)

        else:
            logging.warning(f"No offers found with SKU {data.sku}")

        return root

    def disable_pickup_point(
        self, root: Element, data: "DisablePickupSchema"
    ) -> Element:
        availabilities = root.findall(
            f".//ns:availability[@storeId='{data.store_id}']", namespaces=self.ns
        )
        for availability in availabilities:
            availability.getparent().remove(availability)

        return root

    @staticmethod
    def xml_to_string(root: Element) -> str:
        return tostring(root, encoding="UTF-8", pretty_print=True, xml_declaration=True)

    @staticmethod
    def string_to_xml(xml_string: str) -> Element:
        parser = XMLParser(remove_blank_text=True, remove_comments=False)
        return fromstring(xml_string.encode(), parser=parser)
