import unittest
from plebnet.agent.dna import DNA


class TestDna(unittest.TestCase):

    test_dna = None

    def setUp(self):
        self.test_dna = DNA()

    def tearDown(self):
        self.test_dna = None

    def test_add_provider(self):
        DNA().add_provider("provider1")
        self.assertEqual(DNA().vps, {'provider1': 0.5})

    def test_remove_provider(self):
        DNA().add_provider("provider1")
        DNA().remove_provider("provider1")
        self.assertEqual({}, DNA().vps)


if __name__ == '__main__':
    unittest.main()