"""Utility functions."""

from typing import Tuple
import xml.etree.cElementTree
from xml.etree.cElementTree import Element

import requests

from .type import Namespaces


def parse_source_response_xml(response: requests.Response) -> Tuple[Element, Namespaces]:
    """Parse the XML from the source response."""
    tree = xml.etree.cElementTree.fromstring(response.text)
    # ElementTree has no API to get the namespace so we extract it from the root tag:
    namespaces = dict(ns=tree.tag.split('}')[0][1:])
    return tree, namespaces
