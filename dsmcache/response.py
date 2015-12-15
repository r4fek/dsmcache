
class Response(object):
    """
    Class for storing responses from Memcached server.
    """

    def __init__(self):
        self._data = {}
        self._content = b''

    def write(self, data):
        if data:
            self._content += data

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getitem__(self, item):
        return self._data.get(item)

    @property
    def content(self):
        return self._content

    @property
    def data(self):
        return self._data

    def is_valid(self):
        """
        Return True if response is valid
        :rtype: bool
        """

        # TODO: Would be good to have better error handling. Lack of time :(
        return b'ERROR' not in self._content
