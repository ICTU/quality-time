"""Utility functions."""

import hashlib
import re
import uuid as _uuid
from base64 import b64decode, b64encode
from collections.abc import Callable, Hashable, Iterable, Iterator
from typing import cast, TypeVar

import bottle
import requests
from cryptography.hazmat.backends import default_backend, openssl
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet

# Bandit complains that "Using autolink_html to parse untrusted XML data is known to be vulnerable to XML attacks",
# and Dlint complains 'insecure use of XML modules, prefer "defusedxml"'
# but we give autolink_html clean html, so ignore the warning:
from lxml.html.clean import autolink_html, clean_html  # nosec
from lxml.html import fromstring, tostring  # nosec

from shared.utils.type import ItemId
from shared.utils.functions import iso_timestamp

from .type import URL


class DecryptionError(Exception):
    """Exception to be raised when decryption has failed."""


def check_url_availability(
    url: URL,
    source_parameters: dict[str, str],
    token_validation_path: str,
) -> dict[str, int | str]:
    """Check the availability of the URL."""
    headers = _headers(source_parameters)
    if token_validation_path and "private_token" in source_parameters:
        url = URL(url.rstrip("/") + "/" + token_validation_path.lstrip("/"))
        credentials = None
    else:
        credentials = _basic_auth_credentials(source_parameters)
    try:
        response = requests.get(url, auth=credentials, headers=headers, timeout=10)
        status_code, reason = response.status_code, response.reason
    except Exception as exception_instance:  # noqa: BLE001
        exception_reason = str(exception_instance) or exception_instance.__class__.__name__
        # If the reason contains an errno, only return the errno and accompanying text, and leave out the traceback
        # that led to the error:
        exception_reason = re.sub(r".*(\[errno \-?\d+\] [^\)^']+).*", r"\1", exception_reason, flags=re.IGNORECASE)
        status_code, reason = -1, exception_reason
    return {"status_code": status_code, "reason": reason}


def _basic_auth_credentials(source_parameters) -> tuple[str, str] | None:
    """Return the basic authentication credentials, if any."""
    if private_token := source_parameters.get("private_token", ""):
        return private_token, ""
    username = source_parameters.get("username", "")
    password = source_parameters.get("password", "")
    return (username, password) if username or password else None


def _headers(source_parameters) -> dict:
    """Return the headers for the url-check."""
    if "private_token" in source_parameters:
        private_token = source_parameters["private_token"]
        return {"Private-Token": private_token, "Authorization": f"Bearer {private_token}"}
    return {}


def sanitize_html(html_text: str) -> str:
    """Clean dangerous tags from the HTML and convert urls into anchors."""
    sanitized_html = str(autolink_html(clean_html(html_text)))
    html_tree = fromstring(sanitized_html)
    # Give anchors without target a default target of _blank so they open in a new tab or window:
    for anchor in html_tree.iter("a"):
        keys = anchor.keys()
        if "href" in keys and "target" not in keys:
            anchor.set("target", "_blank")
    sanitized_html = tostring(html_tree, encoding=str)
    # The clean_html function creates HTML elements. That means if the user enters a simple text string it gets
    # enclosed in a <p> tag. Remove it to not confuse users that haven't entered any HTML:
    if sanitized_html.count("<") == 2:  # noqa: PLR2004
        sanitized_html = re.sub("</?p>", "", sanitized_html)
    return sanitized_html


def symmetric_encrypt(message: bytes) -> tuple[bytes, bytes]:
    """Encrypt the given value using Fernet 32 byte key.

    @return: a tuple with the generated key and the encrypted message. Both as bytes.
    """
    key = Fernet.generate_key()
    fernet = Fernet(key)
    token = fernet.encrypt(message)
    return key, token


def symmetric_decrypt(key: bytes, message: bytes) -> bytes:
    """Decrypt the given value using Fernet with a given key.

    @return: decrypted message as b64 encoded bytes.
    """
    fernet = Fernet(key)
    return fernet.decrypt(message)


def asymmetric_encrypt(public_key: str, message: str) -> tuple[str, str]:
    """Encrypts the message using symmetric Fernet encryption.

    The key of the Fernet encryption is encrypted using RSA for public/private key authentication
    and base64 encoded to be able to convert the result into a string.

    @return: a tuple with encrypted Fernet key and encrypted message. Both as string.
    """
    public_key_bytes = public_key.encode()
    message_bytes = message.encode()

    fernet_key, fernet_token = symmetric_encrypt(message_bytes)

    public_key_obj = serialization.load_pem_public_key(public_key_bytes, backend=default_backend())
    public_key_obj = cast(openssl.rsa.RSAPublicKey, public_key_obj)

    encrypted_key = public_key_obj.encrypt(
        fernet_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )
    b64_key = b64encode(encrypted_key)
    return b64_key.decode(), fernet_token.decode()


def asymmetric_decrypt(private_key: str, fernet_key_message: tuple[str, str]) -> str:
    """Decrypts the Fernet key with the provided private rsa key and decrypts the message with the decrypted Fernet key.

    @return: The decrypted message as string
    """
    private_key_bytes = private_key.encode()
    fernet_key_bytes = b64decode(fernet_key_message[0].encode())
    message_bytes = fernet_key_message[1].encode()

    private_key_obj = serialization.load_pem_private_key(private_key_bytes, None, default_backend())
    private_key_obj = cast(openssl.rsa.RSAPrivateKey, private_key_obj)

    decrypted_key = private_key_obj.decrypt(
        fernet_key_bytes,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )
    message = symmetric_decrypt(decrypted_key, message_bytes)

    return message.decode()


Item = TypeVar("Item")


def unique(items: Iterable[Item], get_key: Callable[[Item], Hashable] = lambda item: item) -> Iterator[Item]:
    """Return the unique items in the list."""
    seen: set[Hashable] = set()
    for item in items:
        if (key := get_key(item)) not in seen:
            seen.add(key)
            yield item


def uuid() -> ItemId:
    """Return a UUID."""
    return ItemId(str(_uuid.uuid4()))


def md5_hash(string: str) -> str:
    """Return a md5 hash of the string."""
    md5 = hashlib.md5(string.encode("utf-8"), usedforsecurity=False)
    return md5.hexdigest()


def report_date_time(attribute_name: str = "report_date") -> str:
    """Return the report date requested as query parameter if it's in the past, else return an empty string."""
    if report_date_string := dict(bottle.request.query).get(attribute_name):
        iso_report_date_string = str(report_date_string).replace("Z", "+00:00")
        if iso_report_date_string < iso_timestamp():
            return iso_report_date_string
    return ""
