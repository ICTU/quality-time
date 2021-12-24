"""Utility functions."""

import hashlib
import uuid as _uuid
from base64 import b64decode, b64encode
from collections.abc import Callable, Hashable, Iterable, Iterator
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Tuple, TypeVar, cast

from cryptography.hazmat.backends import default_backend, openssl
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet

from server_utilities.type import Direction, ReportId


def iso_timestamp() -> str:
    """Return the ISO-format version of the current UTC date and time without microseconds."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def days_ago(date_time: datetime) -> int:
    """Return the days since the date/time."""
    return max(0, (datetime.now(tz=date_time.tzinfo) - date_time).days)


def uuid() -> ReportId:
    """Return a UUID."""
    return ReportId(str(_uuid.uuid4()))


def md5_hash(string: str) -> str:
    """Return a md5 hash of the string."""
    return hashlib.md5(string.encode("utf-8")).hexdigest()  # noqa: DUO130, # nosec, Not used for cryptography


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

    @return: a tuple with the generated key and the encrypted message. Both as bytes.
    """
    key = Fernet.generate_key()
    fernet = Fernet(key)
    token = fernet.encrypt(message)
    return key, token


def symmetric_decrypt(key: bytes, message: bytes) -> bytes:
    """
    Decrypt the given value using Fernet with a given key.

    @return: decrypted message as b64 encoded bytes.
    """
    fernet = Fernet(key)
    decrypted_message = fernet.decrypt(message)
    return decrypted_message


def asymmetric_encrypt(public_key: str, message: str) -> tuple[str, str]:
    """
    Encrypts the message using symmetric Fernet encryption.
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
        fernet_key, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    b64_key = b64encode(encrypted_key)
    return b64_key.decode(), fernet_token.decode()


def asymmetric_decrypt(private_key: str, fernet_key_message: Tuple[str, str]) -> str:
    """
    Decrypts the Fernet key with the provided private rsa key.
    Then decrypts the message with the decrypted Fernet key.

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
