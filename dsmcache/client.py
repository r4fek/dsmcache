from __future__ import unicode_literals

import atexit
import logging
import re
import six

from .exceptions import ServerError, InvalidKeyError
from .connection import Host
from .pool import ConnectionPool


METHOD_TO_TEMPLATE = {
    'get': b'get {key}\r\n',
    'set': b'set {key} {flags} {time} {size}\r\n{value}\r\n',
    'flush_all': b'flush_all\r\n'
}

STORED_RE = re.compile(r'^STORED\r\n$')
MAX_KEY_LENGTH = 250

logger = logging.getLogger(__name__)


class Client(object):

    def __init__(self, host, pool_size=20, socket_timeout=None):
        """
        :param host: host/port string. Eg. '127.0.0.1:11211'
        :type: str
        :param pool_size: Size of the connection pool
        :type: int
        :param socket_timeout:
        :type: int
        """

        self._pool = ConnectionPool(Host(host), pool_size=pool_size,
                                    timeout=socket_timeout)

    def __del__(self):
        self.disconnect()

    def get(self, key):
        """
        Get data for given key from Memcached.
        :param key: key to fetch
        :type: str
        """
        return self._send_cmd('get', key=self._check_key(key))

    def set(self, key, value, time=0, flags=0):
        """
        Store data in Memcached.
        :param key:
        :param value:
        :param time: TTL. If 0 then cache forever
        :param flags:
        """

        return self._send_cmd(
                'set', key=self._check_key(key), value=value, flags=flags,
                time=time, size=len(value))

    def flush_all(self):
        return self._send_cmd('flush_all')

    def stats(self):
        return self._send_cmd('stats items')

    def disconnect(self):
        logger.info('Disconnecting connection pool')
        self._pool.close()

    def _send_cmd(self, cmd_name, **kwargs):
        cmd = self._parse_cmd(cmd_name, kwargs)
        response = self._pool.request(cmd)
        return self._parse_response(cmd_name, response)

    @staticmethod
    def _check_key(key):
        """
        Check if key is valid and return it.
        :param key: key to check
        :rtype: str
        """
        if isinstance(key, six.text_type):
            try:
                key = key.encode('ascii')
            except UnicodeEncodeError:
                raise InvalidKeyError('No ascii key: {}'.format(key))

        if b' ' in key:
            raise InvalidKeyError('Spaces in key are not allowed')

        if len(key) > MAX_KEY_LENGTH:
            raise InvalidKeyError(
                    'Max key length is {}'.format(MAX_KEY_LENGTH))
        return key

    @staticmethod
    def _parse_cmd(cmd_name, cmd_args):
        """
        Prepare command to be send to Memcached.
        :param cmd_name: command name like 'set' or 'get'
        :type: str
        :param cmd_args: dict of variables to set in template
        :type: dict
        :return: Parsed command
        :rtype: str
        """
        return METHOD_TO_TEMPLATE[cmd_name].format(**cmd_args)

    @staticmethod
    def _parse_response(cmd_name, response):
        """
        Parse response and return result or raise Server error.
        :param cmd_name: command name
        :type: str
        :param response: Response instance to parse
        :type: Response
        :return: response value
        :raises: ServerError
        """

        if not response.is_valid():
            raise ServerError(response.content)

        if cmd_name == 'get':
            if response.data:
                return response.data.values()[0]
        elif cmd_name == 'set':
            return STORED_RE.match(response.content) and True
