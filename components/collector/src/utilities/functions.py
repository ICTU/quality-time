"""Utility functions."""

from datetime import datetime
import re
from typing import Collection, Tuple
import urllib
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from defusedxml import ElementTree
import requests

from .type import Namespaces, URL


def parse_source_response_xml(response: requests.Response, allowed_root_tags: Collection[str] = None) -> Element:
    """Parse the XML from the source response."""
    tree = ElementTree.fromstring(response.text)
    if allowed_root_tags and tree.tag not in allowed_root_tags:
        raise AssertionError(f'The XML root element should be one of "{allowed_root_tags}" but is "{tree.tag}"')
    return tree


def parse_source_response_xml_with_namespace(
        response: requests.Response, allowed_root_tags: Collection[str] = None) -> Tuple[Element, Namespaces]:
    """Parse the XML with namespace from the source response."""
    tree = parse_source_response_xml(response, allowed_root_tags)
    # ElementTree has no API to get the namespace so we extract it from the root tag:
    namespaces = dict(ns=tree.tag.split('}')[0][1:])
    return tree, namespaces


MEMORY_ADDRESS_RE = re.compile(r" at 0x[0-9abcdef]+>")
TOKEN_RE = re.compile(r"token=[0-9a-zA-Z]+")
KEY_RE = re.compile(r"key=[0-9abcdef]+")


def stable_traceback(traceback: str) -> str:
    """Remove memory addresses from the traceback so make it easier to compare tracebacks."""
    for reg_exp, replacement in [(MEMORY_ADDRESS_RE, ">"), (TOKEN_RE, "token=<redacted>"), (KEY_RE, "key=<redacted>")]:
        traceback = re.sub(reg_exp, replacement, traceback)
    return traceback


def days_ago(date_time: datetime) -> int:
    """Return the days since the date/time."""
    return (datetime.now(tz=date_time.tzinfo) - date_time).days


HASH_RE = re.compile(r"(?i)[a-f0-9]{20,}")


def hashless(url: URL) -> URL:
    """Strip hashes from the url so that it can be used as part of a issue key."""
    scheme, netloc, path, query, fragment = urllib.parse.urlsplit(str(url))
    path = re.sub(HASH_RE, "hashremoved", path)
    query = re.sub(HASH_RE, "hashremoved", query)
    fragment = re.sub(HASH_RE, "hashremoved", fragment)
    return URL(urllib.parse.urlunsplit((scheme, netloc, path, query, fragment)))
