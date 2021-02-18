"""Utility functions."""

import hashlib
import re
import uuid as _uuid
from collections.abc import Callable, Hashable, Iterable, Iterator
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import TypeVar
from base64 import b64encode

import bottle
from cryptography.hazmat.backends import default_backend, openssl
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet

# Bandit complains that "Using autolink_html to parse untrusted XML data is known to be vulnerable to XML attacks",
# and Dlint complains 'insecure use of XML modules, prefer "defusedxml"'
# but we give autolink_html clean html, so ignore the warning:
from lxml.html.clean import autolink_html, clean_html  # noqa: DUO107, # nosec, pylint: disable=no-name-in-module

from server_utilities.type import Direction, ReportId


def iso_timestamp() -> str:
    """Return the ISO-format version of the current UTC date and time without microseconds."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def report_date_time() -> str:
    """Return the report date requested as query parameter if it's in the past, else return an empty string."""
    if report_date_string := dict(bottle.request.query).get("report_date"):
        iso_report_date_string = str(report_date_string).replace("Z", "+00:00")
        if iso_report_date_string < iso_timestamp():
            return iso_report_date_string
    return ""


def uuid() -> ReportId:
    """Return a UUID."""
    return ReportId(str(_uuid.uuid4()))


def md5_hash(string: str) -> str:
    """Return a md5 hash of the string."""
    return hashlib.md5(string.encode("utf-8")).hexdigest()  # noqa: DUO130, # nosec, Not used for cryptography


def sanitize_html(html_text: str) -> str:
    """Clean dangerous tags from the HTML and convert urls into anchors."""
    sanitized_html = str(autolink_html(clean_html(html_text)))
    # The clean_html function creates HTML elements. That means if the user enters a simple text string it gets
    # enclosed in a <p> tag. Remove it to not confuse users that haven't entered any HTML:
    if sanitized_html.count("<") == 2:
        sanitized_html = re.sub("</?p>", "", sanitized_html)
    return sanitized_html


Item = TypeVar("Item")


def unique(items: Iterable[Item], get_key: Callable[[Item], Hashable] = lambda item: item) -> Iterator[Item]:
    """Return the unique items in the list."""
    seen: set[Hashable] = set()
    for item in items:
        if (key := get_key(item)) not in seen:
            seen.add(key)
            yield item


def percentage(numerator: int, denominator: int, direction: Direction) -> int:
    """Return the rounded percentage: numerator / denominator * 100%."""
    if denominator == 0:
        return 0 if direction == "<" else 100
    return int((100 * Decimal(numerator) / Decimal(denominator)).to_integral_value(ROUND_HALF_UP))


def symmetric_encrypt(message: bytes) -> tuple[bytes, bytes]:
    """
    Encrypt the given value using Fernet 32 byte key.
    Returns the generated key and the encrypted message.
    """
    key = Fernet.generate_key()
    fernet = Fernet(key)
    token = fernet.encrypt(message)
    return key, token


def asymmetric_encrypt(public_key_bytes: bytes, message: bytes) -> tuple[str, str]:
    """
    Encrypts the message using symmetric Fernet encryption.
    The key of the Fernet encryption is encrypted using RSA for public/private key authentication
    and base64 encoded to be able to convert the result into a string.
    Returns a tuple with encrypted Fernet key and encrypted message.
    """
    fernet_key, fernet_token = symmetric_encrypt(message)

    public_key_obj = serialization.load_pem_public_key(public_key_bytes, backend=default_backend())
    if not isinstance(public_key_obj, openssl.rsa.RSAPublicKey):
        raise TypeError(f"Public key object should be of type RSAPublicKey, found {type(public_key_obj)}.")

    encrypted_key = public_key_obj.encrypt(
        fernet_key, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    b64_key = b64encode(encrypted_key)
    return b64_key.decode(), fernet_token.decode()
