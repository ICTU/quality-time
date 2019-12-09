"""Unit tests for the authorization routes."""

import logging
import unittest
from unittest.mock import Mock, patch

import bottle
import ldap3
from ldap3.core import exceptions

from database import sessions
from routes import auth


USERNAME = "jodoe"
PASSWORD = "secret"


class AuthTestCase(unittest.TestCase):
    """Base class for authorization tests."""
    def setUp(self):
        self.database = Mock()

    def tearDown(self):
        bottle.response._cookies = None  # pylint: disable=protected-access
        logging.disable(logging.NOTSET)

    def assert_cookie_has_session_id(self):
        """Assert that the response has a cookie with the session id."""
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        return cookie


@patch('bottle.request', Mock(json=dict(username=USERNAME, password=PASSWORD)))
@patch.object(ldap3.Connection, '__exit__', lambda *args: None)
@patch.object(ldap3.Connection, '__enter__')
@patch.object(ldap3.Connection, '__init__')
class LoginTests(AuthTestCase):
    """Unit tests for the login route."""
    def setUp(self):
        super().setUp()
        self.user_email = f"{USERNAME}@example.org"
        self.ldap_root_dn = "dc=example,dc=org"
        self.user_dn = f"cn={USERNAME},{self.ldap_root_dn}"
        self.lookup_user_dn = f"cn=admin,{self.ldap_root_dn}"
        self.log_error_message_template = "LDAP error for %s: %s"
        self.ldap_entry = Mock(entry_dn=self.user_dn)
        self.ldap_entry.userPassword = Mock()
        self.ldap_entry.mail = Mock(value=self.user_email)
        self.ldap_connection = Mock(bind=Mock(return_value=True), search=Mock(), entries=[self.ldap_entry])

    def assert_ldap_connection_search_called(self):
        """Assert that the LDAP connection search method is called with the correct arguments."""
        self.ldap_connection.search.assert_called_with(
            self.ldap_root_dn, f"(|(uid={USERNAME})(cn={USERNAME}))", attributes=['userPassword', 'mail'])

    def assert_ldap_lookup_connection_created(self, connection_mock):
        """Assert that the LDAP lookup connection was created with the lookup user dn and password."""
        self.assertEqual(connection_mock.call_args_list[0][1], dict(user=self.lookup_user_dn, password="admin"))

    def assert_ldap_bind_connection_created(self, connection_mock):
        """Assert that the LDAP bind connection was created with the lookup user dn and password."""
        self.assertEqual(
            connection_mock.call_args_list[1][1], dict(user=self.user_dn, password=PASSWORD, auto_bind=True))

    def assert_log(self, logging_mock, exception, username, email="unknown email"):
        """Assert that the correct error message is logged."""
        self.assertEqual(self.log_error_message_template, logging_mock.call_args[0][0])
        self.assertEqual(f"user {username} <{email}>", logging_mock.call_args[0][1])
        self.assertIsInstance(logging_mock.call_args[0][2], exception)

    def test_successful_login(self, connection_mock, connection_enter):
        """Test successful login."""
        connection_mock.return_value = None
        self.ldap_entry.userPassword.value = b'{SSHA}W841/YybjO4TmqcNTqnBxFKd3SJggaPr'
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=True, email=self.user_email), auth.login(self.database))
        self.assert_cookie_has_session_id()
        self.assert_ldap_lookup_connection_created(connection_mock)
        self.assert_ldap_connection_search_called()

    def test_successful_bind_login(self, connection_mock, connection_enter):
        """Test successful login if ldap server does not reveal password digest."""
        connection_mock.return_value = None
        self.ldap_entry.userPassword.value = None
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=True, email=self.user_email), auth.login(self.database))
        self.assert_cookie_has_session_id()
        self.assert_ldap_lookup_connection_created(connection_mock)
        self.assert_ldap_bind_connection_created(connection_mock)
        self.assert_ldap_connection_search_called()

    @patch.object(logging, 'warning')
    @patch.object(ldap3.Server, '__init__', Mock(side_effect=exceptions.LDAPServerPoolError))
    def test_login_server_error(self, logging_mock, connection_mock, connection_enter):
        """Test login when a server creation error occurs."""
        connection_mock.return_value = None
        self.assertEqual(dict(ok=False, email=''), auth.login(self.database))
        connection_mock.assert_not_called()
        connection_enter.assert_not_called()
        self.assert_log(logging_mock, exceptions.LDAPServerPoolError, USERNAME)

    @patch.object(logging, 'warning')
    def test_login_bind_error(self, logging_mock, connection_mock, connection_enter):
        """Test login when an error of binding dn reader occurs."""
        connection_mock.return_value = None
        self.ldap_connection.bind.return_value = False
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=False, email=''), auth.login(self.database))
        connection_mock.assert_called_once()
        self.ldap_connection.bind.assert_called_once()
        self.assert_log(logging_mock, exceptions.LDAPBindError, self.lookup_user_dn)

    @patch.object(logging, 'warning')
    def test_login_search_error(self, logging_mock, connection_mock, connection_enter):
        """Test login when search error of the login user occurs."""
        connection_mock.return_value = None
        self.ldap_connection.search.side_effect = exceptions.LDAPResponseTimeoutError
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=False, email=''), auth.login(self.database))
        connection_mock.assert_called_once()
        self.ldap_connection.bind.assert_called_once()
        self.assert_log(logging_mock, exceptions.LDAPResponseTimeoutError, USERNAME)

    @patch.object(logging, 'warning')
    def test_login_password_hash_error(self, logging_mock, connection_mock, connection_enter):
        """Test login fails when LDAP password hash is not salted SHA1."""
        connection_mock.return_value = None
        self.ldap_entry.userPassword.value = b'{XSHA}whatever-here'
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=False, email=self.user_email), auth.login(self.database))
        self.assert_ldap_connection_search_called()
        self.assertEqual('Only SSHA LDAP password digest supported!', logging_mock.call_args_list[0][0][0])
        self.assert_log(logging_mock, exceptions.LDAPInvalidAttributeSyntaxResult, self.user_dn, self.user_email)

    @patch.object(logging, 'warning')
    def test_login_wrong_password(self, logging_mock, connection_mock, connection_enter):
        """Test login when search error of the login user occurs."""
        connection_mock.return_value = None
        self.ldap_entry.userPassword.value = b'{SSHA}W841/abcdefghijklmnopqrstuvwxyz0'
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=False, email=self.user_email), auth.login(self.database))
        self.assert_ldap_connection_search_called()
        self.assert_log(logging_mock, exceptions.LDAPInvalidCredentialsResult, self.user_dn, self.user_email)


class LogoutTests(AuthTestCase):
    """Unit tests for the logout route."""
    @patch.object(sessions, 'delete')
    @patch('bottle.request')
    def test_logout(self, request_mock, delete_mock):
        """Test successful logout."""
        session_id = "the session id"
        request_mock.get_cookie = Mock(return_value=session_id)
        self.assertEqual(dict(ok=True), auth.logout(self.database))
        cookie = self.assert_cookie_has_session_id()
        self.assertTrue(cookie.find(session_id) > 0)
        self.assertRegex(cookie.upper(), r".+MON,\s*0*1\s*JAN\S*\s*0*1")
        delete_mock.assert_called_with(self.database, session_id)
