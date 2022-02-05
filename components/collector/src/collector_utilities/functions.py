"""Utility functions."""

import contextlib
import hashlib
import re
import time
import urllib
from collections.abc import Collection, Generator
from datetime import datetime
from typing import cast
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from defusedxml import ElementTree

from .type import URL, Namespaces, Response


async def parse_source_response_xml(response: Response, allowed_root_tags: Collection[str] = None) -> Element:
    """Parse the XML from the source response."""
    tree = cast(Element, ElementTree.fromstring(await response.text(), forbid_dtd=False))
    if allowed_root_tags and tree.tag not in allowed_root_tags:
        raise AssertionError(f'The XML root element should be one of "{allowed_root_tags}" but is "{tree.tag}"')
    return tree


async def parse_source_response_xml_with_namespace(
    response: Response, allowed_root_tags: Collection[str] = None
) -> tuple[Element, Namespaces]:
    """Parse the XML with namespace from the source response."""
    tree = await parse_source_response_xml(response, allowed_root_tags)
    # ElementTree has no API to get the namespace so we extract it from the root tag:
    namespaces = dict(ns=tree.tag.split("}")[0][1:])
    return tree, namespaces


Substitution = tuple[re.Pattern[str], str]
MEMORY_ADDRESS_SUB: Substitution = (re.compile(r" at 0x[0-9abcdef]+>"), ">")
TOKEN_SUB: Substitution = (re.compile(r"token=[^&]+"), "token=<redacted>")
KEY_SUB: Substitution = (re.compile(r"key=[0-9abcdef]+"), "key=<redacted>")
HASH_SUB: Substitution = (re.compile(r"(?i)[a-f0-9]{20,}"), "hashremoved")


def stable_traceback(traceback: str) -> str:
    """Remove memory addresses from the traceback so make it easier to compare tracebacks."""
    for reg_exp, replacement in [MEMORY_ADDRESS_SUB, TOKEN_SUB, KEY_SUB]:
        traceback = re.sub(reg_exp, replacement, traceback)
    return traceback


def tokenless(url: str) -> str:
    """Strip private tokens from (text with) urls."""
    return re.sub(TOKEN_SUB[0], TOKEN_SUB[1], url)


def hashless(url: URL) -> URL:
    """Strip hashes from the url so that it can be used as part of a issue key."""
    scheme, netloc, path, query, fragment = urllib.parse.urlsplit(str(url))
    path = re.sub(HASH_SUB[0], HASH_SUB[1], path)
    query = re.sub(HASH_SUB[0], HASH_SUB[1], query)
    fragment = re.sub(HASH_SUB[0], HASH_SUB[1], fragment)
    return URL(urllib.parse.urlunsplit((scheme, netloc, path, query, fragment)))


def md5_hash(string: str) -> str:
    """Return a md5 hash of the string."""
    return hashlib.md5(string.encode("utf-8")).hexdigest()  # noqa: DUO130, # nosec, Not used for cryptography


def sha1_hash(string: str) -> str:
    """Return a sha1 hash of the string."""
    return hashlib.sha1(string.encode("utf-8")).hexdigest()  # noqa: DUO130, # nosec, Not used for cryptography


def days_ago(date_time: datetime) -> int:
    """Return the days since the date/time."""
    return (datetime.now(tz=date_time.tzinfo) - date_time).days


def days_to_go(date_time: datetime) -> int:
    """Return the days remaining until the date/time."""
    return (date_time - datetime.now(tz=date_time.tzinfo)).days


def is_regexp(string: str) -> bool:
    """Return whether the string looks like a regular expression."""
    return bool(set("$^?.+*[]") & set(string))


def match_string_or_regular_expression(string: str, strings_and_or_regular_expressions: Collection[str]) -> bool:
    """Return whether the string is equal to one of the strings or matches one of the regular expressions."""
    for string_or_regular_expression in strings_and_or_regular_expressions:
        if is_regexp(string_or_regular_expression):
            if re.match(string_or_regular_expression, string):
                return True
        else:
            if string_or_regular_expression == string:
                return True
    return False


class Clock:  # pylint: disable=too-few-public-methods
    """Class to keep track of time."""

    def __init__(self) -> None:
        self.start = time.perf_counter()
        self.duration = 0.0

    def stop(self) -> None:
        """Stop the clock."""
        self.duration = time.perf_counter() - self.start


@contextlib.contextmanager
def timer() -> Generator[Clock, None, None]:
    """Timer context manager."""
    clock = Clock()
    yield clock
    clock.stop()
