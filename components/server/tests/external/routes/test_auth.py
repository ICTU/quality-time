"""Unit tests for the authorization routes."""

import logging
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import bottle
import ldap3
from ldap3.core import exceptions

from external.database import sessions
from external.routes import login, logout, get_public_key

USERNAME = "john-doe"
PASSWORD = "secret"


class AuthTestCase(unittest.TestCase):  # skipcq: PTC-W0046
    """Base class for authorization tests."""

    def setUp(self):
        """Override to set up a mock database."""
        self.database = Mock()
        self.database.secrets.find_one.return_value = {"public_key": "this_is_a_public_key"}

    def tearDown(self):
        """Override to remove the cookies and reset the logging."""
        bottle.response._cookies = None  # pylint: disable=protected-access
        logging.disable(logging.NOTSET)

    def assert_cookie_has_session_id(self):
        """Assert that the response has a cookie with the session id."""
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        return cookie

    def test_get_public_key(self, *_):
        """Test that the correct public key is returned as dict."""
        public_key = get_public_key(self.database)
        self.assertDictEqual(public_key, {"public_key": "this_is_a_public_key"})


@patch("bottle.request", Mock(json=dict(username=USERNAME, password=PASSWORD)))
@patch.object(ldap3.Connection, "__exit__", lambda *args: None)
@patch.object(ldap3.Connection, "__enter__")
@patch.object(ldap3.Connection, "__init__")
class LoginTests(AuthTestCase):
    """Unit tests for the login route."""

    NOW = datetime(2021, 2, 21, 21, 8, 0, tzinfo=timezone.utc)
    MOCK_DATETIME = Mock(now=Mock(return_value=NOW))
    USER_EMAIL = f"{USERNAME}@example.org"
    LDAP_ROOT_DN = "dc=example,dc=org"
    USER_DN = f"cn={USERNAME},{LDAP_ROOT_DN}"
    LOOKUP_USER_DN = f"cn=admin,{LDAP_ROOT_DN}"
    LOG_ERROR_MESSAGE_TEMPLATE = "LDAP error: %s"

    def setUp(self):
        """Extend to add a mock LDAP."""
        super().setUp()
        self.database.reports_overviews.find_one.return_value = dict(_id="id")
        self.ldap_entry = Mock(entry_dn=self.USER_DN)
        self.ldap_entry.userPassword = Mock()
        self.ldap_entry.mail = Mock(value=self.USER_EMAIL)
        self.ldap_connection = Mock(bind=Mock(return_value=True), search=Mock(), entries=[self.ldap_entry])
        self.login_ok = dict(
            ok=True, email=self.USER_EMAIL, session_expiration_datetime=(self.NOW + timedelta(hours=24)).isoformat()
        )
        self.login_nok = dict(
            ok=False, email="", session_expiration_datetime=datetime.min.replace(tzinfo=timezone.utc).isoformat()
        )

    def assert_ldap_connection_search_called(self):
        """Assert that the LDAP connection search method is called with the correct arguments."""
        self.ldap_connection.search.assert_called_with(
            self.LDAP_ROOT_DN, f"(|(uid={USERNAME})(cn={USERNAME}))", attributes=["userPassword", "mail"]
        )

    def assert_ldap_lookup_connection_created(self, connection_mock):
        """Assert that the LDAP lookup connection was created with the lookup user dn and password."""
        self.assertEqual(connection_mock.call_args_list[0][1], dict(user=self.LOOKUP_USER_DN, password="admin"))

    def assert_ldap_bind_connection_created(self, connection_mock):
        """Assert that the LDAP bind connection was created with the lookup user dn and password."""
        self.assertEqual(
            connection_mock.call_args_list[1][1], dict(user=self.USER_DN, password=PASSWORD, auto_bind=True)
        )

    def assert_log(self, logging_mock, exception):
        """Assert that the correct error message is logged."""
        self.assertEqual(self.LOG_ERROR_MESSAGE_TEMPLATE, logging_mock.call_args[0][0])
        self.assertIsInstance(logging_mock.call_args[0][1], exception)

    @patch("external.routes.auth.datetime", MOCK_DATETIME)
    def test_successful_forwardauth_login(self, connection_mock, connection_enter):
        """Test successful login from forwarded authentication header."""
        connection_mock.return_value = None
        with patch.dict(
            "os.environ", {"FORWARD_AUTH_ENABLED": "True", "FORWARD_AUTH_HEADER": "X-Forwarded-User"}
        ), patch("bottle.request.get_header", Mock(return_value=self.USER_EMAIL)):
            self.assertEqual(self.login_ok, login(self.database))
        self.assert_cookie_has_session_id()
        connection_mock.assert_not_called()
        connection_enter.assert_not_called()

    def test_forwardauth_login_no_header(self, connection_mock, connection_enter):
        """Test failed login if forwarded authentication is enabled but no header is present."""
        connection_mock.return_value = None
        with patch.dict(
            "os.environ", {"FORWARD_AUTH_ENABLED": "True", "FORWARD_AUTH_HEADER": "X-Forwarded-User"}
        ), patch("bottle.request.get_header", Mock(return_value=None)):
            self.assertEqual(self.login_nok, login(self.database))
        connection_mock.assert_not_called()
        connection_enter.assert_not_called()

    @patch("external.routes.auth.datetime", MOCK_DATETIME)
    def test_successful_login(self, connection_mock, connection_enter):
        """Test successful login."""
        connection_mock.return_value = None
        self.ldap_entry.userPassword.value = b"{SSHA}W841/YybjO4TmqcNTqnBxFKd3SJggaPr"
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(self.login_ok, login(self.database))
        self.assert_cookie_has_session_id()
        self.assert_ldap_lookup_connection_created(connection_mock)
        self.assert_ldap_connection_search_called()

    @patch("external.routes.auth.datetime", MOCK_DATETIME)
    def test_successful_bind_login(self, connection_mock, connection_enter):
        """Test successful login if ldap server does not reveal password digest."""
        connection_mock.return_value = None
        self.ldap_entry.userPassword.value = None
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(self.login_ok, login(self.database))
        self.assert_cookie_has_session_id()
        self.assert_ldap_lookup_connection_created(connection_mock)
        self.assert_ldap_bind_connection_created(connection_mock)
        self.assert_ldap_connection_search_called()

    @patch.object(logging, "warning")
    @patch.object(ldap3.Server, "__init__", Mock(side_effect=exceptions.LDAPServerPoolError))
    def test_login_server_error(self, logging_mock, connection_mock, connection_enter):
        """Test login when a server creation error occurs."""
        connection_mock.return_value = None
        self.assertEqual(self.login_nok, login(self.database))
        connection_mock.assert_not_called()
        connection_enter.assert_not_called()
        self.assert_log(logging_mock, exceptions.LDAPServerPoolError)

    @patch.object(logging, "warning")
    def test_login_bind_error(self, logging_mock, connection_mock, connection_enter):
        """Test login when an error of binding dn reader occurs."""
        connection_mock.return_value = None
        self.ldap_connection.bind.return_value = False
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(self.login_nok, login(self.database))
        connection_mock.assert_called_once()
        self.ldap_connection.bind.assert_called_once()
        self.assert_log(logging_mock, exceptions.LDAPBindError)

    @patch.object(logging, "warning")
    def test_login_search_error(self, logging_mock, connection_mock, connection_enter):
        """Test login when search error of the login user occurs."""
        connection_mock.return_value = None
        self.ldap_connection.search.side_effect = exceptions.LDAPResponseTimeoutError
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(self.login_nok, login(self.database))
        connection_mock.assert_called_once()
        self.ldap_connection.bind.assert_called_once()
        self.assert_log(logging_mock, exceptions.LDAPResponseTimeoutError)

    @patch.object(logging, "warning")
    def test_login_password_hash_error(self, logging_mock, connection_mock, connection_enter):
        """Test login fails when LDAP password hash is not salted SHA1."""
        connection_mock.return_value = None
        self.ldap_entry.userPassword.value = b"{XSHA}whatever-here"
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(self.login_nok, login(self.database))
        self.assert_ldap_connection_search_called()
        self.assertEqual("Only SSHA LDAP password digest supported!", logging_mock.call_args_list[0][0][0])
        self.assert_log(logging_mock, exceptions.LDAPInvalidAttributeSyntaxResult)

    @patch.object(logging, "warning")
    def test_login_wrong_password(self, logging_mock, connection_mock, connection_enter):
        """Test login when search error of the login user occurs."""
        connection_mock.return_value = None
        self.ldap_entry.userPassword.value = b"{SSHA}W841/abcdefghijklmnopqrstuvwxyz0"
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(self.login_nok, login(self.database))
        self.assert_ldap_connection_search_called()
        self.assert_log(logging_mock, exceptions.LDAPInvalidCredentialsResult)


class LogoutTests(AuthTestCase):
    """Unit tests for the logout route."""

    @patch.object(sessions, "delete")
    @patch("bottle.request")
    def test_logout(self, request_mock, delete_mock):
        """Test successful logout."""
        session_id = "the session id"
        request_mock.get_cookie = Mock(return_value=session_id)
        self.assertEqual(dict(ok=True), logout(self.database))
        cookie = self.assert_cookie_has_session_id()
        self.assertTrue(cookie.find(session_id) > 0)
        self.assertRegex(cookie.upper(), r".+MON,\s*0*1\s*JAN\S*\s*0*1")
        delete_mock.assert_called_with(self.database, session_id)
