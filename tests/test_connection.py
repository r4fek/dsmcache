import socket
from unittest import TestCase

from mock import patch, Mock

from dsmcache.connection import Host, Connection
from dsmcache.exceptions import InvalidAddressError, InvalidPortError


class HostTestCase(TestCase):
    host_str = '127.0.0.1:11211'

    def test_init(self):
        host = Host(self.host_str)
        self.assertEqual(host._ip, '127.0.0.1')
        self.assertEqual(host._port, 11211)

    def test_str(self):
        host = Host(self.host_str)
        self.assertEqual(str(host), self.host_str)

    def test_repr(self):
        host = Host(self.host_str)
        self.assertEqual(repr(host), '<Host: {}>'.format(self.host_str))

    def test_ip(self):
        host = Host(self.host_str)
        self.assertEqual(host.ip, '127.0.0.1')

    def test_port(self):
        host = Host(self.host_str)
        self.assertEqual(host._ip, '127.0.0.1')
        self.assertEqual(host.port, 11211)

    def test_address(self):
        host = Host(self.host_str)
        self.assertEqual(host.address, ('127.0.0.1', 11211))

    def test_parse_ok(self):
        host = Host(self.host_str)
        host._parse(self.host_str)

    def test_parse_invalid_address(self):
        host = Host(self.host_str)

        with self.assertRaises(InvalidAddressError) as cm:
            host._parse('12:.0.0.1:11211')

        self.assertEqual(cm.exception.message, 'Invalid address')

    def test_parse_invalid_port(self):
        host = Host(self.host_str)

        with self.assertRaises(InvalidPortError) as cm:
            host._parse('127.0.0.1:xx')

        self.assertEqual(cm.exception.message, 'Invalid port')


class ConnectionTestCase(TestCase):

    def setUp(self):
        self.socket_patch = patch('dsmcache.connection.socket')
        self.socket_mock = self.socket_patch.start()
        self.host = Host('127.0.0.1:11211')
        self.connection = Connection(self.host)

    def tearDown(self):
        self.socket_patch.stop()
        self.connection.close()

    def test_init(self):
        connection = Connection(self.host, socket_timeout=10, retry_timeout=5)

        self.assertEqual(connection._host, self.host)
        self.assertEqual(connection._socket_timeout, 10)
        self.assertEqual(connection._retry_timeout, 5)
        self.assertEqual(connection._socket, None)
        self.assertEqual(connection._dead_ts, 0)

    @patch('dsmcache.connection.Connection._check_dead')
    def test_connect_dead(self, check_dead_mock):
        check_dead_mock.return_value = True

        self.assertIsNone(self.connection.connect())

    @patch('dsmcache.connection.Connection._check_dead')
    def test_connect_connected_before(self, check_dead_mock):
        self.connection._socket = Mock()
        check_dead_mock.return_value = False

        self.assertEqual(self.connection.connect(), self.connection._socket)

    @patch('dsmcache.connection.Connection._check_dead')
    def test_connect_socket_timeout(self, check_dead_mock):

        self.socket_mock.socket.return_value.connect.side_effect = \
            socket.timeout()
        check_dead_mock.return_value = False
        self.assertEqual(self.connection._socket, None)
        with self.assertRaises(socket.timeout):
            self.connection.connect()

        self.socket_mock.socket.assert_called_once_with(
                self.socket_mock.AF_INET, self.socket_mock.SOCK_STREAM)
        self.socket_mock.socket.return_value.connect.assert_called_once_with(
                self.connection._host.address)

    @patch('dsmcache.connection.Connection._check_dead')
    def test_connect_socket_error(self, check_dead_mock):
        self.socket_mock.socket.return_value.connect.side_effect = \
            socket.error()
        check_dead_mock.return_value = False

        with self.assertRaises(socket.error):
            self.connection.connect()

        self.socket_mock.socket.assert_called_once_with(
                self.socket_mock.AF_INET, self.socket_mock.SOCK_STREAM)
        self.socket_mock.socket.return_value.connect.assert_called_once_with(
                self.connection._host.address)

    @patch('dsmcache.connection.Connection._check_dead')
    def test_connect_ok(self, check_dead_mock):
        check_dead_mock.return_value = False
        self.assertEqual(self.connection.connect(),
                         self.socket_mock.socket.return_value)

    def test_send(self):
        pass

    def test_is_alive(self):
        pass

    def test_check_dead_not_dead(self):
        pass

    def test_check_dead_is_dead(self):
        pass

    def test_mark_socket_dead(self):
        pass

    def test_close_no_socket(self):
        pass

    def test_close(self):
        pass
