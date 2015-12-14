from unittest import TestCase

from dsmcache.client import Client


class GetSetTestCase(TestCase):

    def setUp(self):
        self.pool_size = 2
        self.client = Client('0.0.0.0:11211', pool_size=self.pool_size)
        self.client.flush_all()

    def tearDown(self):
        self.client.disconnect()

    def test_client_get_miss(self):
        self.assertEqual(self.client.get('notexist'), None)

    def test_client_get_hit(self):
        self.assertTrue(self.client.set('key', 'val'))
        self.assertEqual(self.client.get('key'), 'val')

    def test_client_last_set_wins(self):
        self.assertTrue(self.client.set('key', 'val'))
        self.assertTrue(self.client.set('key', 'val2'))
        self.assertEqual(self.client.get('key'), 'val2')

    def test_pool_works(self):
        for i in range(self.pool_size*5):
            self.assertTrue(self.client.set('key%s' % i, 'val'))
            self.assertEqual(self.client.get('key%s' % i), 'val')

    def test_wrong_address(self):
        client = Client('0.0.0.0:11111')
        self.assertFalse(client.set('a', 'b'))
        self.assertIsNone(client.get('a'))
