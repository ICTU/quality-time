"""Unit tests for the authorization routes."""

import logging
import unittest
from unittest.mock import MagicMock, Mock, patch

import ldap3
from ldap3.core import exceptions

import bottle
from database import sessions
from routes import auth

# pylint: disable=too-many-arguments

class LoginTests(unittest.TestCase):
    """Unit tests for the login route."""
    def setUp(self):
        self.database = Mock()
        self.environ_get = MagicMock(
            side_effect=["dc=example,dc=org", "ldap://localhost:389", "admin", "admin", "ldap://localhost:389"])

    def tearDown(self):
        bottle.response._cookies = None  # pylint: disable=protected-access
        logging.disable(logging.NOTSET)

    @patch.object(ldap3.Connection, '__exit__')
    @patch.object(ldap3.Connection, '__enter__')
    @patch.object(ldap3.Connection, '__init__')
    @patch.object(ldap3.Server, '__init__')
    @patch('bottle.request')
    def test_successful_login(self, request_json_mock, server_mock, connection_mock, connection_enter, connection_exit):
        """Test successful login."""
        environ_get = MagicMock(side_effect=["dc=example,dc=org", 'http://www.quality-time.my-org.org:5001',
                                             "admin", "admin", 'http://www.quality-time.my-org.org:5001'])
        request_json_mock.json = dict(username="jodoe", password="secret")
        server_mock.return_value = None
        connection_mock.return_value = None
        connection_exit.return_value = None
        fake_con = MagicMock()
        fake_con.bind = MagicMock(return_value=True)
        fake_con.search = MagicMock()
        ldap_entry = Mock()
        ldap_entry.userPassword = Mock()
        ldap_entry.userPassword.value = b'{SSHA}W841/YybjO4TmqcNTqnBxFKd3SJggaPr'
        fake_con.entries = [ldap_entry]
        connection_enter.return_value = fake_con
        with patch("os.environ.get", environ_get):
            self.assertEqual(dict(ok=True), auth.login(self.database))

        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertTrue("domain=" in cookie.lower())
        self.assertEqual(connection_mock.call_args[1],
                         {'user': 'cn=admin,dc=example,dc=org', 'password': 'admin'})
        fake_con.search.assert_called_with("dc=example,dc=org", '(|(uid=jodoe)(cn=jodoe))',
                                           attributes=['cn', 'userPassword'])

    @patch.object(ldap3.Connection, '__exit__')
    @patch.object(ldap3.Connection, '__enter__')
    @patch.object(ldap3.Connection, '__init__')
    @patch.object(ldap3.Server, '__init__')
    @patch('bottle.request')
    def test_successful_bind_login(self, request_json_mock, server_mock, connection_mock, connection_enter,
                                   connection_exit):
        """Test successful login if ldap server does not reveal password digest."""
        request_json_mock.json = dict(username="jodoe", password="secret")
        server_mock.return_value = None
        connection_mock.return_value = None
        connection_exit.return_value = None
        fake_con = MagicMock()
        fake_con.bind = MagicMock(return_value=True)
        fake_con.search = MagicMock()
        ldap_entry = Mock()
        ldap_entry.userPassword = Mock()
        ldap_entry.userPassword.value = None
        ldap_entry.cn.value = 'concrete cn value, e.g. Jo Doe'
        fake_con.entries = [ldap_entry]
        connection_enter.return_value = fake_con
        with patch("os.environ.get", self.environ_get):
            self.assertEqual(dict(ok=True), auth.login(self.database))

        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertFalse("domain=" in cookie.lower())
        self.assertEqual(connection_mock.call_args_list[0][1],
                         {'user': 'cn=admin,dc=example,dc=org', 'password': 'admin'})
        self.assertEqual(connection_mock.call_args_list[1][1],
                         {'user': 'cn=concrete cn value, e.g. Jo Doe,dc=example,dc=org',
                          'password': 'secret', 'auto_bind': True})
        fake_con.search.assert_called_with(
            "dc=example,dc=org", '(|(uid=jodoe)(cn=jodoe))', attributes=['cn', 'userPassword'])


    @patch.object(ldap3.Connection, '__exit__')
    @patch.object(ldap3.Connection, '__enter__')
    @patch.object(ldap3.Connection, '__init__')
    @patch.object(ldap3.Server, '__init__')
    @patch('bottle.request')
    def test_successful_login_local(self, request_json_mock, server_mock, connection_mock, connection_enter,
                                    connection_exit):
        """Test successful login."""
        request_json_mock.json = dict(username="jodoe", password="secret")
        server_mock.return_value = None
        connection_mock.return_value = None
        connection_exit.return_value = None
        fake_con = MagicMock()
        fake_con.bind = MagicMock(return_value=True)
        fake_con.search = MagicMock()
        ldap_entry = Mock()
        ldap_entry.userPassword = Mock()
        ldap_entry.userPassword.value = b'{SSHA}W841/YybjO4TmqcNTqnBxFKd3SJggaPr'
        fake_con.entries = [ldap_entry]
        connection_enter.return_value = fake_con
        with patch("os.environ.get", self.environ_get):
            self.assertEqual(dict(ok=True), auth.login(self.database))

        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertFalse("domain=" in cookie.lower())
        fake_con.search.assert_called_with(
            "dc=example,dc=org", '(|(uid=jodoe)(cn=jodoe))', attributes=['cn', 'userPassword'])

    @patch.object(logging, 'warning')
    @patch.object(ldap3.Connection, '__init__')
    @patch.object(ldap3.Server, '__init__')
    @patch('bottle.request')
    def test_login_server_error(self, request_json_mock, server_mock, connection_mock, logging_mock):
        """Test login when a server creation error occurs."""
        request_json_mock.json = dict(username="jodoe", password="secret")
        server_mock.side_effect = exceptions.LDAPServerPoolError
        connection_mock.return_value = None
        with patch("os.environ.get", self.environ_get):
            self.assertEqual(dict(ok=False), auth.login(self.database))
        connection_mock.assert_not_called()
        self.assertEqual('LDAP error for cn=%s,%s: %s', logging_mock.call_args[0][0])
        self.assertEqual('jodoe', logging_mock.call_args[0][1])
        self.assertEqual("dc=example,dc=org", logging_mock.call_args[0][2])
        self.assertIsInstance(logging_mock.call_args[0][3], exceptions.LDAPServerPoolError)

    @patch.object(logging, 'warning')
    @patch.object(ldap3.Connection, '__exit__')
    @patch.object(ldap3.Connection, '__enter__')
    @patch.object(ldap3.Connection, '__init__')
    @patch.object(ldap3.Server, '__init__')
    @patch('bottle.request')
    def test_login_bind_error(self, request_json_mock, server_mock, connection_mock, connection_enter,
                              connection_exit, logging_mock):
        """Test login when an error of binding dn reader occurs."""
        request_json_mock.json = dict(username="jodoe", password="secret")
        server_mock.return_value = None
        connection_mock.return_value = None
        connection_exit.return_value = None
        fake_con = MagicMock()
        fake_con.bind = MagicMock(return_value=False)
        connection_enter.return_value = fake_con
        with patch("os.environ.get", self.environ_get):
            self.assertEqual(dict(ok=False), auth.login(self.database))

        connection_mock.assert_called_once()
        fake_con.bind.assert_called_once()
        self.assertEqual('LDAP error for cn=%s,%s: %s', logging_mock.call_args[0][0])
        self.assertEqual('admin', logging_mock.call_args[0][1])
        self.assertEqual("dc=example,dc=org", logging_mock.call_args[0][2])
        self.assertIsInstance(logging_mock.call_args[0][3], exceptions.LDAPBindError)

    @patch.object(logging, 'warning')
    @patch.object(ldap3.Connection, '__exit__')
    @patch.object(ldap3.Connection, '__enter__')
    @patch.object(ldap3.Connection, '__init__')
    @patch.object(ldap3.Server, '__init__')
    @patch('bottle.request')
    def test_login_search_error(self, request_json_mock, server_mock, connection_mock, connection_enter,
                                connection_exit, logging_mock):
        """Test login when search error of the login user occurs."""
        request_json_mock.json = dict(username="jodoe", password="secret")
        server_mock.return_value = None
        connection_mock.return_value = None
        connection_exit.return_value = None
        fake_con = MagicMock()
        fake_con.bind = MagicMock(return_value=True)
        fake_con.search = MagicMock(side_effect=exceptions.LDAPResponseTimeoutError)
        connection_enter.return_value = fake_con
        with patch("os.environ.get", self.environ_get):
            self.assertEqual(dict(ok=False), auth.login(self.database))

        connection_mock.assert_called_once()
        fake_con.bind.assert_called_once()
        self.assertEqual('LDAP error for cn=%s,%s: %s', logging_mock.call_args[0][0])
        self.assertEqual('jodoe', logging_mock.call_args[0][1])
        self.assertEqual("dc=example,dc=org", logging_mock.call_args[0][2])
        self.assertIsInstance(logging_mock.call_args[0][3], exceptions.LDAPResponseTimeoutError)

    @patch.object(logging, 'warning')
    @patch.object(ldap3.Connection, '__exit__')
    @patch.object(ldap3.Connection, '__enter__')
    @patch.object(ldap3.Connection, '__init__')
    @patch.object(ldap3.Server, '__init__')
    @patch('bottle.request')
    def test_login_password_hash_error(self, request_json_mock, server_mock, connection_mock, connection_enter,
                                       connection_exit, logging_mock):
        """Test login fails when LDAP password hash is not salted SHA1."""
        request_json_mock.json = dict(username="jodoe", password="secret")
        server_mock.return_value = None
        connection_mock.return_value = None
        connection_exit.return_value = None
        fake_con = MagicMock()
        fake_con.bind = MagicMock(return_value=True)
        fake_con.search = MagicMock()
        ldap_entry = Mock()
        ldap_entry.userPassword = Mock()
        ldap_entry.userPassword.value = b'{XSHA}whatever-here'
        fake_con.entries = [ldap_entry]
        connection_enter.return_value = fake_con
        with patch("os.environ.get", self.environ_get):
            self.assertEqual(dict(ok=False), auth.login(self.database))
        fake_con.search.assert_called_with(
            "dc=example,dc=org", '(|(uid=jodoe)(cn=jodoe))', attributes=['cn', 'userPassword'])
        self.assertEqual('Only SSHA LDAP password digest supported!', logging_mock.call_args_list[0][0][0])
        self.assertEqual('LDAP error for cn=%s,%s: %s', logging_mock.call_args_list[1][0][0])
        self.assertEqual('jodoe', logging_mock.call_args_list[1][0][1])
        self.assertEqual("dc=example,dc=org", logging_mock.call_args_list[1][0][2])
        self.assertIsInstance(logging_mock.call_args_list[1][0][3], exceptions.LDAPInvalidAttributeSyntaxResult)

    @patch.object(logging, 'warning')
    @patch.object(ldap3.Connection, '__exit__')
    @patch.object(ldap3.Connection, '__enter__')
    @patch.object(ldap3.Connection, '__init__')
    @patch.object(ldap3.Server, '__init__')
    @patch('bottle.request')
    def test_login_wrong_password(self, request_json_mock, server_mock, connection_mock, connection_enter,
                                  connection_exit, logging_mock):
        """Test login when search error of the login user occurs."""
        request_json_mock.json = dict(username="jodoe", password="wrong password!")
        server_mock.return_value = None
        connection_mock.return_value = None
        connection_exit.return_value = None
        fake_con = MagicMock()
        fake_con.bind = MagicMock(return_value=True)
        fake_con.search = MagicMock()
        ldap_entry = Mock()
        ldap_entry.userPassword = Mock()
        ldap_entry.userPassword.value = b'{SSHA}W841/YybjO4TmqcNTqnBxFKd3SJggaPr'
        fake_con.entries = [ldap_entry]
        connection_enter.return_value = fake_con
        with patch("os.environ.get", self.environ_get):
            self.assertEqual(dict(ok=False), auth.login(self.database))
        fake_con.search.assert_called_with(
            "dc=example,dc=org", '(|(uid=jodoe)(cn=jodoe))', attributes=['cn', 'userPassword'])
        logging_mock.assert_not_called()

class LogoutTests(unittest.TestCase):
    """Unit tests for the logout route."""
    @patch.object(sessions, 'delete')
    @patch('bottle.request')
    def test_logout(self, request_mock, delete_mock):
        """Test successful logout."""
        request_mock.get_cookie = MagicMock(return_value='the session id')
        database = MagicMock()
        self.assertEqual(dict(ok=True), auth.logout(database))
        cookie = str(bottle.response._cookies)  # pylint: disable=protected-access
        self.assertTrue(cookie.startswith("Set-Cookie: session_id="))
        self.assertTrue(cookie.find("the session id") > 0)
        self.assertRegex(cookie.upper(), r".+MON,\s*0*1\s*JAN\S*\s*0*1")
        delete_mock.assert_called_with(database, 'the session id')
