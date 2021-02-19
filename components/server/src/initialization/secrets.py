"""Generate a public and private key pair if it doesn't already exist."""

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


EXPORT_FIELDS_KEYS_NAME = "export_fields_keys"
EXPORT_FIELDS_USAGE_DESCRIPTION = """
Use this public/private key fields when exporting sensitive
content (like api credentials) from the Quality-Time database.
They are stored in plain text in the database.
"""


def initialize_secrets(database):
    """Make sure public and private keys exist."""
    # do nothing if it already exists
    if database.secrets.find_one({"name": EXPORT_FIELDS_KEYS_NAME}):
        return

    # else: create new public/private key pair and insert it
    # private key
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
    privkey = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # public key
    public_key = private_key.public_key()
    pubkey = public_key.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    database.secrets.insert(
        {
            "name": EXPORT_FIELDS_KEYS_NAME,
            "description": EXPORT_FIELDS_USAGE_DESCRIPTION,
            "private_key": privkey.decode(),
            "public_key": pubkey.decode(),
        }
    )
