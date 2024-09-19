import time
from xml.etree.ElementTree import Element, SubElement


root = Element("kaspi_catalog")
root.set("xmlns", "de")
root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
root.set("date", str(int(time.time())))
root.set("xsi:schemaLocation", f"{4} {33}")

SubElement(root, "company").text = "store_name"
SubElement(root, "merchantid").text = "merchant_id"
offers_element = SubElement(root, "offers")
offers_element.text = ""

from src.services.xml_services import XMLService

xml_service = XMLService()

print(xml_service.xml_to_string(root))
