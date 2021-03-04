"""Unit tests for the util module."""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from base64 import b64decode

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from server_utilities.functions import (
    asymmetric_decrypt,
    asymmetric_encrypt,
    iso_timestamp,
    report_date_time,
    symmetric_decrypt,
    symmetric_encrypt,
    uuid,
)


class UtilTests(unittest.TestCase):
    """Unit tests for the utility methods."""

    def test_iso_timestamp(self):
        """Test that the iso timestamp has the correct format."""
        expected_time_stamp = "2020-03-03T10:04:05+00:00"
        with patch("server_utilities.functions.datetime") as date_time:
            date_time.now.return_value = datetime(2020, 3, 3, 10, 4, 5, 567, tzinfo=timezone.utc)
            self.assertEqual(expected_time_stamp, iso_timestamp())

    def test_uuid(self):
        """Test the expected length of the uuid."""
        self.assertEqual(36, len(uuid()))

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
        """Test wether message that has been encrypted using symmetric_encrypt ca be decrypted."""
        # encryption
        test_message = b"this is a test message"
        key, encrypted_message = symmetric_encrypt(test_message)

        # decryption
        message = symmetric_decrypt(key, encrypted_message)
        self.assertEqual(message, test_message)

    def test_asymmetric_encrypt(self):
        """Test wether message is encrypted using public/private keys."""
        # get public and private keys
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
        public_key = private_key.public_key()
        pubkey = public_key.public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
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
        """Test wether message that has been encrypted using asymmetric_encrypt ca be decrypted."""
        # get public and private keys
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096, backend=default_backend())
        privkey = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_key = private_key.public_key()
        pubkey = public_key.public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # encryption
        test_message = "this is a test message"
        encrypted_key, encrypted_message = asymmetric_encrypt(pubkey.decode(), test_message)

        # decryption
        message = asymmetric_decrypt(privkey.decode(), (encrypted_key, encrypted_message))

        self.assertEqual(message, test_message)


@patch("server_utilities.functions.bottle.request")
class ReportDateTimeTest(unittest.TestCase):
    """Unit tests for the report_datetime method."""

    def setUp(self):
        """Override to setup the 'current' time."""
        self.now = datetime(2019, 3, 3, 10, 4, 5, 567, tzinfo=timezone.utc)
        self.expected_time_stamp = "2019-03-03T10:04:05+00:00"

    def test_report_date_time(self, request):
        """Test that the report datetime can be parsed from the HTTP request."""
        request.query = dict(report_date="2019-03-03T10:04:05Z")
        self.assertEqual(self.expected_time_stamp, report_date_time())

    def test_missing_report_date_time(self, request):
        """Test that the report datetime is empty if it's not present in the request."""
        request.query = {}
        self.assertEqual("", report_date_time())

    def test_future_report_date_time(self, request):
        """Test that the report datetime is empty if it's a future date."""
        request.query = dict(report_date="3000-01-01T00:00:00Z")
        self.assertEqual("", report_date_time())
