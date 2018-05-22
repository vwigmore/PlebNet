import unittest
from appdirs import user_config_dir
import os
from cloudomate.util.settings import Settings
from plebnet.utilities import fake_generator


'These filepaths are already specified in the source code and cannot be changed here'
file1 = os.path.join(user_config_dir(), 'plebnet.json')
file2 = os.path.join(user_config_dir(), 'child_config0.cfg')


class TestFakeGenerator(unittest.TestCase):

    def setUp(self):
        if os.path.isfile(file1):
            os.remove(file1)
        if os.path.isfile(file2):
            os.remove(file2)

    def tearDown(self):
        if os.path.isfile(file1):
            os.remove(file1)
        if os.path.isfile(file2):
            os.remove(file2)

    def test_generate_child_account_file_created(self):
        fake_generator.generate_child_account()
        self.assertTrue(os.path.isfile(file2))

    def test_generate_child_has_content(self):
        fake_generator.generate_child_account()
        account = Settings()
        account.read_settings(os.path.join(user_config_dir(), 'child_config0.cfg'))

        self.assertIsNotNone(account.get('user', 'email'))
        self.assertIsNotNone(account.get('user', 'firstname'))
        self.assertIsNotNone(account.get('user', 'lastname'))
        self.assertIsNotNone(account.get('user', 'companyname'))
        self.assertIsNotNone(account.get('user', 'phonenumber'))
        self.assertIsNotNone(account.get('user', 'password'))

        self.assertIsNotNone(account.get('address', 'address'))
        self.assertIsNotNone(account.get('address', 'city'))
        self.assertIsNotNone(account.get('address', 'state'))
        self.assertIsNotNone(account.get('address', 'countrycode'))
        self.assertIsNotNone(account.get('address', 'zipcode'))

        self.assertIsNotNone(account.get('server', 'root_password'))
        self.assertEqual(account.get('server', 'ns1'), 'ns1')
        self.assertEqual(account.get('server', 'ns2'), 'ns2')
        self.assertIsNotNone(account.get('server', 'hostname'))


if __name__ == '__main__':
    unittest.main()