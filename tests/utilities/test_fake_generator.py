import unittest

from plebnet.utilities import fake_generator


class TestFakeGenerator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_useless(self):
        self.assertEquals(2*4, 8)


if __name__ == '__main__':
    unittest.main()