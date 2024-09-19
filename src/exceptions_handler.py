import functools
import logging
from json.decoder import JSONDecodeError
from typing import Callable
from lxml.etree import XMLSyntaxError, XPathEvalError, ParseError


def process_exception_handler(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except JSONDecodeError as json_exception:
            logging.error(f"Invalid JSON in message body: {str(json_exception)}")
            raise json_exception
        except ValueError as value_exception:
            logging.error(f"Invalid data format: {str(value_exception)}")
            raise value_exception
        except XMLSyntaxError as xml_syntax_error:
            logging.error(f"XML Syntax Error: {str(xml_syntax_error)}")
            raise xml_syntax_error
        except XPathEvalError as xpath_error:
            logging.error(f"XPath Evaluation Error: {str(xpath_error)}")
            raise xpath_error
        except ParseError as parse_error:
            logging.error(f"XML Parsing Error: {str(parse_error)}")
            raise parse_error
        except AttributeError as attr_error:
            logging.error(
                f"Attribute Error (possibly missing XML element): {str(attr_error)}"
            )
            raise attr_error
        except TypeError as type_error:
            logging.error(
                f"Type Error (possibly incorrect data type in XML operation): {str(type_error)}"
            )
            raise type_error
        except Exception as exception:
            logging.error(f"Unexpected error processing message: {str(exception)}")
            raise exception

    return wrapper
