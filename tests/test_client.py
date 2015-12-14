from __future__ import unicode_literals
from mock import patch, Mock

from unittest import TestCase

from dsmcache.client import Client


class ClientTestCase(TestCase):

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

    def test_get(self):
        pass

    def test_get_invalid_key(self):
        pass

    def test_set(self):
        pass

    def test_set_invalid_key(self):
        pass

    def test_set_invalid_value(self):
        pass

    def test_send_cmd(self):
        pass

    def test_parse_cmd(self):
        pass

    def test_check_key_valid(self):
        pass

    def test_check_key_invalid(self):
        pass
