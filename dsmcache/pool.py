from __future__ import unicode_literals

from six.moves.queue import Queue, Full, Empty

from .exceptions import EmptyPoolError, ClosedPoolError
from .connection import Connection, DEFAULT_SOCKET_TIMEOUT


class ConnectionPool(object):

    QueueCls = Queue
    ConnectionCls = Connection

    def __init__(self, host, pool_size=20, timeout=DEFAULT_SOCKET_TIMEOUT):
        self._host = host
        self._pool_size = pool_size
        self._timeout = timeout
        self._pool = self.QueueCls(pool_size)

        # TODO: creating all `pool_size` connections on startup probably isn't
        # a good idea
        for _ in range(self._pool_size):
            self._pool.put(self._new_connection())

    def __repr__(self):
        return '<ConnectionPool: {}>'.format(self._host)

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()
        return False

    def _new_connection(self):
        """
        Create new connection
        :return: newly created Connection instance
        :rtype: Connection
        """

        connection = Connection(self._host, socket_timeout=self._timeout)
        return connection

    def _put_connection(self, conn):
        """
        Put connection back to the pool
        :param conn: Connection instance
        """
        try:
            self._pool.put(conn, block=False)
            return
        except Full:
            # Do not put connection to pool if it's full
            pass
        except AttributeError:
            pass

        if conn:
            conn.close()

    def _get_connection(self):
        connection = None
        try:
            connection = self._pool.get(timeout=self._timeout)
        except Empty:
            pass
        except AttributeError:
            raise ClosedPoolError('Pool is already closed')

        return connection or self._new_connection()

    def close(self):
        """
        Close all connections and make pool unusable.
        """
        pool = self._pool
        self._pool = None

        while True:
            try:
                conn = pool.get(block=False)
            except Empty:
                return
            if conn:
                conn.close()

    def request(self, cmd):
        """
        Get connection instance from the queue and send `cmd` through it
        :param cmd: command to send
        :type: str
        :return: Response instance
        :rtype: Response
        """
        connection = None

        try:
            connection = self._pool.get(timeout=self._timeout)
            connection.connect()  # if not already connected
            connection.send(cmd)
            response = connection.read()
        except Empty:
            raise EmptyPoolError('Pool is empty')
        except AttributeError:
            raise ClosedPoolError('Pool is already closed')
        finally:
            # put connection back to the pool
            if connection:
                self._put_connection(connection)

        return response
