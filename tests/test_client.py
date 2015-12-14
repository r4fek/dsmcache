from __future__ import unicode_literals
from mock import patch, Mock

from unittest import TestCase

from dsmcache.client import Client
from dsmcache.exceptions import InvalidKeyError


class ClientTestCase(TestCase):

    def setUp(self):
        self.client = Client('0.0.0.0')

    def tearDown(self):
        self.client.disconnect()

    @patch('dsmcache.client.ConnectionPool')
    @patch('dsmcache.client.Host')
    def test_init(self, host_mock, connection_pool_mock):
        host = '127.0.0.1:11211'
        pool_size = 10
        socket_timeout = 3
        connection_pool_mock.return_value = Mock()
        host_mock.return_value = Mock()

        client = Client(host, pool_size=pool_size,
                        socket_timeout=socket_timeout)

        connection_pool_mock.assert_called_once_with(
            host_mock.return_value, pool_size=pool_size, timeout=socket_timeout
        )
        host_mock.assert_called_once_with(host)
        self.assertEqual(client._pool, connection_pool_mock.return_value)

    @patch('dsmcache.client.Client._send_cmd')
    @patch('dsmcache.client.Client._check_key')
    def test_get(self, check_key_mock, send_mock):
        check_key_mock.return_value = 'key'
        self.client.get('key')

        check_key_mock.assert_called_once_with('key')
        send_mock.assert_called_once_with(
                'get', key=check_key_mock.return_value)

    @patch('dsmcache.client.Client._send_cmd')
    @patch('dsmcache.client.Client._check_key')
    def test_get_invalid_key(self, check_key_mock, send_mock):
        check_key_mock.side_effect = InvalidKeyError('invalid key')

        with self.assertRaises(InvalidKeyError) as cm:
            self.client.get('key')

        self.assertEqual(cm.exception, check_key_mock.side_effect)
        self.assertFalse(send_mock.called)

    @patch('dsmcache.client.Client._send_cmd')
    @patch('dsmcache.client.Client._check_key')
    def test_set(self, check_key_mock, send_mock):
        check_key_mock.return_value = 'key'
        self.client.set('key', 'value', time=0, flags=0)

        check_key_mock.assert_called_once_with('key')
        send_mock.assert_called_once_with(
                'set', key=check_key_mock.return_value, value='value', flags=0,
                time=0, size=len('value'))

    @patch('dsmcache.client.Client._send_cmd')
    @patch('dsmcache.client.Client._check_key')
    def test_set_invalid_key(self, check_key_mock, send_mock):
        check_key_mock.side_effect = InvalidKeyError('invalid key')

        with self.assertRaises(InvalidKeyError) as cm:
            self.client.set('key', 'v')

        self.assertEqual(cm.exception, check_key_mock.side_effect)
        self.assertFalse(send_mock.called)

    def test_send_cmd(self):
        pass

    def test_parse_cmd(self):
        pass

    def test_check_key_valid(self):
        pass

    def test_check_key_invalid(self):
        pass
