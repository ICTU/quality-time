"""Unit tests for the authorization routes."""

import logging
import unittest
from unittest.mock import Mock, patch

import bottle
import ldap  # pylint: disable=import-error

from src.routes import auth


class LoginTests(unittest.TestCase):
    """Unit tests for the login route."""
    def setUp(self):
        logging.disable()
        self.database = Mock()
        self.ldap_server = Mock()
        self.ldap_server.search_s.return_value = [
            ('cn=John Doe,ou=users,dc=example,dc=org', {'cn': [b'John Doe'], 'uid': [b'jodoe', b'jodoe1']})]
        self.lookup_json = Mock(json=dict(username="admin", password="admin"))
        self.invalid_creds_json = Mock(json=dict(username="wrong", password="wrong"))
        self.valid_creds_uid_json = Mock(json=dict(username="jodoe", password="secret"))
        self.valid_creds_cn_json = Mock(json=dict(username="John Doe", password="secret"))

    def tearDown(self):
        bottle.response._cookies = None  # pylint: disable=protected-access
        logging.disable(logging.NOTSET)

    def test_successful_login(self):
        """Test successful login."""
        with patch("os.environ.get", Mock(return_value="http://www.quality-time.my-org.org:5001")):
            with patch("bottle.request", return_value=self.valid_creds_uid_json):
                with patch("ldap.initialize", return_value=self.ldap_server):
                    self.assertEqual(dict(ok=True), auth.login(self.database))
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertTrue("domain=" in cookie.lower())

    def test_successful_login_localhost_uid(self):
        """Test successful login on localhost."""
        with patch("bottle.request", return_value=self.valid_creds_uid_json):
            with patch("ldap.initialize", return_value=self.ldap_server):
                self.assertEqual(dict(ok=True), auth.login(self.database))
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertFalse("domain=" in cookie.lower())

    def test_successful_login_localhost_cn(self):
        """Test successful login on localhost."""
        with patch("bottle.request", return_value=self.valid_creds_cn_json):
            with patch("ldap.initialize", return_value=self.ldap_server):
                self.assertEqual(dict(ok=True), auth.login(self.database))
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertFalse("domain=" in cookie.lower())

    def test_lookup_user_simple_bind_s_failure(self):
        self.ldap_server.simple_bind_s.side_effect = ldap.INVALID_CREDENTIALS
        with patch("bottle.request", return_value=self.valid_creds_uid_json):
            with patch("ldap.initialize", return_value=self.ldap_server):
                self.assertEqual(dict(ok=False), auth.login(self.database))

    def test_simple_search_s_failure(self):
        self.ldap_server.search_s.side_effect = ldap.INVALID_CREDENTIALS
        with patch("bottle.request", return_value=self.invalid_creds_json):
            with patch("ldap.initialize", return_value=self.ldap_server):
                self.assertEqual(dict(ok=False), auth.login(self.database))

    def test_unsuccessful_login_localhost_cn(self):
        """Test unsuccessful login on localhost."""
        self.ldap_server.simple_bind_s.side_effect = [None, ldap.INVALID_CREDENTIALS]
        with patch("bottle.request", return_value=self.invalid_creds_json):
            with patch("ldap.initialize", return_value=self.ldap_server):
                self.assertEqual(dict(ok=False), auth.login(self.database))

    def test_failed_login(self):
        """Test failed login."""
        self.ldap_server.search_s.return_value = []
        with patch("bottle.request", return_value=self.lookup_json):
            with patch("ldap.initialize", return_value=self.ldap_server):
                self.assertEqual(dict(ok=False), auth.login(self.database))


class LogoutTests(unittest.TestCase):
    """Unit tests for the logout route."""
    def test_logout(self):
        """Test successful logout."""
        database = Mock()
        self.assertEqual(dict(ok=True), auth.logout(database))
