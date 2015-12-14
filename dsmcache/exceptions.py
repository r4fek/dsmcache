
class HostException(Exception):
    pass


class InvalidAddressError(HostException):
    """
    Exception raised if address is invalid
    """


class InvalidPortError(HostException):
    """
    Exception raised if port is invalid
    """


class ConnectionPoolException(Exception):
    """
    Base class for all connection pool exceptions
    """


class EmptyPoolError(ConnectionPoolException):
    """
    Exception raised if connection pool is empty
    """


class ClosedPoolError(ConnectionPoolException):
    """
    Exception raised if connection pool is closed
    """


class ServerError(Exception):
    """
    Base class for all server errors
    """


class InvalidKeyError(Exception):
    """
    Exception raised if key is invalid
    """
