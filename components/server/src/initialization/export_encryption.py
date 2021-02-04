"""Generate a public and private key pair if it doesn't already exist"""

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def init_public_private_keys():
    """make sure public and private keys exist"""

    # private key
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
    privkey = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open("credentials_export_private_key.pem", "wb") as file:
        file.write(privkey)

    # public key
    public_key = private_key.public_key()
    pubkey = public_key.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open("credentials_export_public_key.pem", "wb") as file:
        file.write(pubkey)


if __name__ == "__main__":
    init_public_private_keys()
