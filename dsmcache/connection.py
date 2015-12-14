from __future__ import unicode_literals
import logging
import re
import socket
import time

from .response import Response
from .exceptions import InvalidPortError, InvalidAddressError


DEFAULT_MC_PORT = 11211
DEFAULT_SOCKET_TIMEOUT = 3
logger = logging.getLogger(__name__)


class Host(object):

    def __init__(self, host_str):
        """
        :param host_str: either IP address of the host or IP with port
        in format 'IP:PORT'
        """
        self._ip, self._port = self._parse(host_str)

    def __str__(self):
        return '{}:{}'.format(self._ip, self._port)

    def __repr__(self):
        return '<Host: {}:{}>'.format(self._ip, self._port)

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    @property
    def address(self):
        return self._ip, self._port

    @staticmethod
    def _parse(host_str):
        addr_port = host_str.split(':')

        if not re.match(r'[^:]+', addr_port[0]) or len(addr_port) > 2:
            raise InvalidAddressError('Invalid address')

        if len(addr_port) == 1:
            return addr_port[0], DEFAULT_MC_PORT
        else:
            try:
                port = int(addr_port[1])
            except ValueError:
                raise InvalidPortError('Invalid port')
            return addr_port[0], port


class Connection(object):
    """
    Class representing connection to Memcached server
    """

    def __init__(self, host, socket_timeout=DEFAULT_SOCKET_TIMEOUT,
                 retry_timeout=10):
        self._host = host
        self._socket_timeout = socket_timeout
        self._retry_timeout = retry_timeout
        self._socket = None
        self._dead_ts = 0
        self._buffer = b''

    def connect(self):
        """
        Connect to a socket
        :return: socket instance or None if unable to connect
        :rtype: socket.socket | None
        """

        if self._check_dead():
            return
        if self._socket:
            return self._socket

        self._buffer = b''
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._socket_timeout)

        try:
            self._socket.connect(self._host.address)
        except (socket.timeout, socket.error) as exc:
            self._mark_socket_dead(str(exc))
            return

        return self._socket

    def send(self, cmd):
        try:
            self._socket.sendall(cmd)
        except (AttributeError, socket.error, socket.timeout) as exc:
            self._mark_socket_dead(str(exc))
            return

    def _read(self, length=None):
        """
        Return `length` bytes from the server or if length is None
        read one line delimited by `\r\n` and return.
        :param length: number of bytes to read from the socket.
        :rtype: str | None
        """
        response = None

        while response is None:
            if length:
                if len(self._buffer) >= length:
                    response = self._buffer[:length]
                    self._buffer = self._buffer[length:]
            else:
                index = self._buffer.find('\r\n')
                if index != -1:
                    response = self._buffer[:index+2]
                    self._buffer = self._buffer[index+2:]

            if response is None:
                try:
                    tmp = self._socket.recv(4096)
                except (AttributeError, socket.error, socket.timeout) as exc:
                    self._mark_socket_dead(str(exc))
                    return

                if not tmp:
                    self._mark_socket_dead('Server error')
                else:
                    self._buffer += tmp
        return response

    def read(self):
        self._buffer = b''
        response = Response()
        line = self._read()
        response.write(line)

        if line and 'VALUE' in line:
            while line != 'END\r\n':
                header = line.split()
                if len(header) == 4 and header[0] == 'VALUE':
                    key = header[1]
                    length = int(header[3])
                    line = self._read(length)
                    response.write(line)
                    response[key] = line
                line = self._read()
                response.write(line)
        return response

    def is_alive(self):
        return not self._check_dead()

    def _check_dead(self):
        """
        Return True if socket is marked as dead
        """
        return self._dead_ts > time.time()

    def _mark_socket_dead(self, reason):
        self._dead_ts = time.time() + self._retry_timeout
        logger.debug('Socket is dead with reason: {}'.format(reason))
        self.close()

    def close(self):
        if self._socket:
            self._socket.close()
            self._socket = None
