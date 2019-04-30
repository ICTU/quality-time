"""Utility functions."""

from datetime import datetime
import re
from typing import Tuple
import xml.etree.cElementTree
from xml.etree.cElementTree import Element

import requests

from .type import Namespaces


def parse_source_response_xml(response: requests.Response) -> Element:
    """Parse the XML from the source response."""
    return xml.etree.cElementTree.fromstring(response.text)


def parse_source_response_xml_with_namespace(response: requests.Response) -> Tuple[Element, Namespaces]:
    """Parse the XML with namespace from the source response."""
    tree = parse_source_response_xml(response)
    # ElementTree has no API to get the namespace so we extract it from the root tag:
    namespaces = dict(ns=tree.tag.split('}')[0][1:])
    return tree, namespaces


MEMORY_ADDRESS_RE = re.compile(r" at 0x[0-9abcdef]+>")
TOKEN_RE = re.compile(r"token=[0-9abcdef]+")
KEY_RE = re.compile(r"key=[0-9abcdef]+")


def stable_traceback(traceback: str) -> str:
    """Remove memory addresses from the traceback so make it easier to compare tracebacks."""
    for reg_exp, replacement in [(MEMORY_ADDRESS_RE, ">"), (TOKEN_RE, "token=<redacted>"), (KEY_RE, "key=<redacted>")]:
        traceback = re.sub(reg_exp, replacement, traceback)
    return traceback


def days_ago(date_time: datetime) -> int:
    """Return the days since the date/time."""
    return (datetime.now(tz=date_time.tzinfo) - date_time).days
