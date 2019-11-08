"""Unit tests for the authorization routes."""

import logging
import unittest
from unittest.mock import Mock, patch

import bottle
import ldap3
from ldap3.core import exceptions

from database import sessions
from routes import auth


@patch.object(ldap3.Connection, '__enter__')
@patch.object(ldap3.Connection, '__exit__', lambda *args: None)
@patch('bottle.request', Mock(json=dict(username="jodoe", password="secret")))
class LoginTests(unittest.TestCase):
    """Unit tests for the login route."""
    def setUp(self):
        self.database = Mock()
        self.ldap_entry = Mock(entry_dn="cn=jodoe,dc=example,dc=org")
        self.ldap_entry.userPassword = Mock()
        self.ldap_connection = Mock(bind=Mock(return_value=True), search=Mock(), entries=[self.ldap_entry])

    def tearDown(self):
        bottle.response._cookies = None  # pylint: disable=protected-access
        logging.disable(logging.NOTSET)

    @patch.object(ldap3.Connection, '__init__')
    def test_successful_login(self, connection_mock, connection_enter):
        """Test successful login."""
        connection_mock.return_value = None
        self.ldap_entry.userPassword.value = b'{SSHA}W841/YybjO4TmqcNTqnBxFKd3SJggaPr'
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=True), auth.login(self.database))
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertEqual(connection_mock.call_args[1], dict(user='cn=admin,dc=example,dc=org', password='admin'))
        self.ldap_connection.search.assert_called_with(
            "dc=example,dc=org", '(|(uid=jodoe)(cn=jodoe))', attributes=['userPassword'])

    @patch.object(ldap3.Connection, '__init__')
    def test_successful_bind_login(self, connection_mock, connection_enter):
        """Test successful login if ldap server does not reveal password digest."""
        connection_mock.return_value = None
        self.ldap_entry.userPassword.value = None
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=True), auth.login(self.database))
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertEqual(
            connection_mock.call_args_list[0][1], dict(user='cn=admin,dc=example,dc=org', password='admin'))
        self.assertEqual(
            connection_mock.call_args_list[1][1],
            dict(user='cn=jodoe,dc=example,dc=org', password='secret', auto_bind=True))
        self.ldap_connection.search.assert_called_with(
            "dc=example,dc=org", '(|(uid=jodoe)(cn=jodoe))', attributes=['userPassword'])

    @patch.object(ldap3.Connection, '__init__', Mock(return_value=None))
    def test_successful_login_local(self, connection_enter):
        """Test successful login."""
        self.ldap_entry.userPassword.value = b'{SSHA}W841/YybjO4TmqcNTqnBxFKd3SJggaPr'
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=True), auth.login(self.database))
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.ldap_connection.search.assert_called_with(
            "dc=example,dc=org", '(|(uid=jodoe)(cn=jodoe))', attributes=['userPassword'])

    @patch.object(logging, 'warning')
    @patch.object(ldap3.Connection, '__init__')
    @patch.object(ldap3.Server, '__init__', Mock(side_effect=exceptions.LDAPServerPoolError))
    def test_login_server_error(self, connection_mock, logging_mock, connection_enter):
        """Test login when a server creation error occurs."""
        connection_mock.return_value = None
        self.assertEqual(dict(ok=False), auth.login(self.database))
        connection_mock.assert_not_called()
        connection_enter.assert_not_called()
        self.assertEqual('LDAP error for user %s: %s', logging_mock.call_args[0][0])
        self.assertEqual('jodoe', logging_mock.call_args[0][1])
        self.assertIsInstance(logging_mock.call_args[0][2], exceptions.LDAPServerPoolError)

    @patch.object(logging, 'warning')
    @patch.object(ldap3.Connection, '__init__')
    def test_login_bind_error(self, connection_mock, logging_mock, connection_enter):
        """Test login when an error of binding dn reader occurs."""
        connection_mock.return_value = None
        self.ldap_connection.bind.return_value = False
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=False), auth.login(self.database))
        connection_mock.assert_called_once()
        self.ldap_connection.bind.assert_called_once()
        self.assertEqual('LDAP error for user %s: %s', logging_mock.call_args[0][0])
        self.assertEqual('cn=admin,dc=example,dc=org', logging_mock.call_args[0][1])
        self.assertIsInstance(logging_mock.call_args[0][2], exceptions.LDAPBindError)

    @patch.object(logging, 'warning')
    @patch.object(ldap3.Connection, '__init__')
    def test_login_search_error(self, connection_mock, logging_mock, connection_enter):
        """Test login when search error of the login user occurs."""
        connection_mock.return_value = None
        self.ldap_connection.search.side_effect = exceptions.LDAPResponseTimeoutError
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=False), auth.login(self.database))
        connection_mock.assert_called_once()
        self.ldap_connection.bind.assert_called_once()
        self.assertEqual('LDAP error for user %s: %s', logging_mock.call_args[0][0])
        self.assertEqual('jodoe', logging_mock.call_args[0][1])
        self.assertIsInstance(logging_mock.call_args[0][2], exceptions.LDAPResponseTimeoutError)

    @patch.object(logging, 'warning')
    @patch.object(ldap3.Connection, '__init__', Mock(return_value=None))
    def test_login_password_hash_error(self, logging_mock, connection_enter):
        """Test login fails when LDAP password hash is not salted SHA1."""
        self.ldap_entry.userPassword.value = b'{XSHA}whatever-here'
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=False), auth.login(self.database))
        self.ldap_connection.search.assert_called_with(
            "dc=example,dc=org", '(|(uid=jodoe)(cn=jodoe))', attributes=['userPassword'])
        self.assertEqual('Only SSHA LDAP password digest supported!', logging_mock.call_args_list[0][0][0])
        self.assertEqual('LDAP error for user %s: %s', logging_mock.call_args_list[1][0][0])
        self.assertEqual('jodoe', logging_mock.call_args[0][1])
        self.assertIsInstance(logging_mock.call_args_list[1][0][2], exceptions.LDAPInvalidAttributeSyntaxResult)

    @patch.object(logging, 'warning')
    @patch.object(ldap3.Connection, '__init__', Mock(return_value=None))
    def test_login_wrong_password(self, logging_mock, connection_enter):
        """Test login when search error of the login user occurs."""
        self.ldap_entry.userPassword.value = b'{SSHA}W841/abcdefghijklmnopqrstuvwxyz0'
        connection_enter.return_value = self.ldap_connection
        self.assertEqual(dict(ok=False), auth.login(self.database))
        self.ldap_connection.search.assert_called_with(
            "dc=example,dc=org", '(|(uid=jodoe)(cn=jodoe))', attributes=['userPassword'])
        logging_mock.assert_not_called()


class LogoutTests(unittest.TestCase):
    """Unit tests for the logout route."""
    @patch.object(sessions, 'delete')
    @patch('bottle.request')
    def test_logout(self, request_mock, delete_mock):
        """Test successful logout."""
        request_mock.get_cookie = Mock(return_value='the session id')
        database = Mock()
        self.assertEqual(dict(ok=True), auth.logout(database))
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertTrue(cookie.find("the session id") > 0)
        self.assertRegex(cookie.upper(), r".+MON,\s*0*1\s*JAN\S*\s*0*1")
        delete_mock.assert_called_with(database, 'the session id')
