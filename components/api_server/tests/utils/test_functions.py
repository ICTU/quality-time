"""Unit tests for the utils module."""

import unittest
from base64 import b64decode
from datetime import datetime, UTC
from unittest.mock import patch

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from utils.functions import (
    asymmetric_decrypt,
    asymmetric_encrypt,
    md5_hash,
    report_date_time,
    sanitize_html,
    symmetric_decrypt,
    symmetric_encrypt,
    uuid,
)


class UtilTests(unittest.TestCase):
    """Unit tests for the utility methods."""

    URL = "https://example-url.org/"

    def test_uuid(self):
        """Test the expected length of the uuid."""
        self.assertEqual(36, len(uuid()))

    def test_md5_hash(self):
        """Test that the hash works."""
        self.assertEqual("bc9189406be84ec297464a514221406d", md5_hash("XXX"))

    def test_sanitize_html(self):
        """Test that URLs are converted to anchors."""
        self.assertEqual(f'<p><a href="{self.URL}" target="_blank">{self.URL}</a></p>', sanitize_html(self.URL))

    def test_sanitize_html_does_mot_convert_text_to_html(self):
        """Test that text without HTML does not get converted to HTML."""
        self.assertEqual("Text.", sanitize_html("Text."))

    def test_sanitize_html_does_not_change_target(self):
        """Test that existing target attributes are not changed."""
        self.assertEqual(
            f'<a href="{self.URL}" target="_top">{self.URL}</a>',
            sanitize_html(f'<a href="{self.URL}" target="_top">{self.URL}</a>'),
        )
        self.assertEqual(
            f'<a href="{self.URL}" target="_blank">{self.URL}</a>',
            sanitize_html(f'<a href="{self.URL}" target="_blank">{self.URL}</a>'),
        )

    def test_sanitize_html_does_not_add_target_without_href(self):
        """Test that a target attribute is not added when there's no href attribute."""
        self.assertEqual(f"<a>{self.URL}</a>", sanitize_html(f"<a>{self.URL}</a>"))


@patch("utils.functions.bottle.request")
class ReportDateTimeTest(unittest.TestCase):
    """Unit tests for the report_datetime method."""

    def setUp(self):
        """Override to setup the 'current' time."""
        self.now = datetime(2019, 3, 3, 10, 4, 5, 567, tzinfo=UTC)
        self.expected_time_stamp = "2019-03-03T10:04:05+00:00"

    def test_report_date_time(self, request):
        """Test that the report datetime can be parsed from the HTTP request."""
        request.query = {"report_date": "2019-03-03T10:04:05Z"}
        self.assertEqual(self.expected_time_stamp, report_date_time())

    def test_missing_report_date_time(self, request):
        """Test that the report datetime is empty if it's not present in the request."""
        request.query = {}
        self.assertEqual("", report_date_time())

    def test_future_report_date_time(self, request):
        """Test that the report datetime is empty if it's a future date."""
        request.query = {"report_date": "3000-01-01T00:00:00Z"}
        self.assertEqual("", report_date_time())


class TestEncryption(unittest.TestCase):
    """Unit tests for the encryption and decryption utility functions."""

    def test_symmetric_encryption(self):
        """Test wether message is encrypted using and can be decrypted."""
        # encryption
        test_message = b"this is a test message"
        key, encrypted_message = symmetric_encrypt(test_message)
        self.assertNotEqual(test_message, encrypted_message)

        # decryption
        fernet = Fernet(key)
        decrypted_message = fernet.decrypt(encrypted_message)
        self.assertEqual(decrypted_message, test_message)

    def test_symmetric_decryption(self):
        """Test whether the message that has been encrypted using symmetric_encrypt can be decrypted."""
        # encryption
        test_message = b"this is a test message"
        key, encrypted_message = symmetric_encrypt(test_message)

        # decryption
        message = symmetric_decrypt(key, encrypted_message)
        self.assertEqual(message, test_message)

    def test_asymmetric_encrypt(self):
        """Test whether the message is encrypted using public/private keys."""
        # get public and private keys
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
        public_key = private_key.public_key()
        pubkey = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # encryption
        test_message = "this is a test message"
        encrypted_key, encrypted_message = asymmetric_encrypt(pubkey.decode(), test_message)
        self.assertNotEqual(test_message, encrypted_message)

        # decryption
        decrypted_key = private_key.decrypt(
            b64decode(encrypted_key.encode()),
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
        )
        fernet = Fernet(decrypted_key)
        decrypted_message = fernet.decrypt(encrypted_message.encode()).decode()

        self.assertEqual(decrypted_message, test_message)

    def test_asymmetric_decrypt(self):
        """Test whether the message that has been encrypted using asymmetric_encrypt can be decrypted."""
        # get public and private keys
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
        privkey = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_key = private_key.public_key()
        pubkey = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # encryption
        test_message = "this is a test message"
        encrypted_key, encrypted_message = asymmetric_encrypt(pubkey.decode(), test_message)

        # decryption
        message = asymmetric_decrypt(privkey.decode(), (encrypted_key, encrypted_message))

        self.assertEqual(message, test_message)
