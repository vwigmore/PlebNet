import unittest
import mock
from mock.mock import MagicMock
from appdirs import user_config_dir
import os
import sys
from plebnet.utilities import logger
from plebnet.settings import plebnet_settings

# test_file = os.path.join(user_config_dir(), 'plebnet.logs')
# test_path = user_config_dir()
# test_name = plebnet_settings.get_instance().logger_filename()
file = plebnet_settings.get_instance().logger_file()
# test_name = '.log'
# test_file = os.path.join(test_path, test_name)
# test_file = plebnet_settings.get_instance().logger_file()
msg1 = "this is a log"
msg2 = "this is another log"
msg3 = "this is a nice line"
msg4 = "this is a beautiful line of text"


class TestLogger(unittest.TestCase):

    def setUp(self):
        # logger.reset()
        logger.suppress_print = True
        if os.path.isfile(file):
            os.remove(file)
        #ensure logging is allowed
        plebnet_settings.get_instance().active_logger("1")

    def tearDown(self):
        if os.path.isfile(file):
            os.remove(file)
        # disable logging for further tests
        plebnet_settings.get_instance().active_logger("0")

    def test_generate_file(self):
        self.assertFalse(os.path.isfile(file))
        logger.log(msg1)
        self.assertTrue(os.path.isfile(file))

    def test_add_logs(self):
        logger.log(msg1)
        logger.log(msg2)
        self.assertTrue(msg1 in open(file).read())
        self.assertTrue(msg2 in open(file).read())

    def test_add_multiple_logs(self):
        logger.log(msg1)
        logger.warning(msg2)
        logger.success(msg3)
        logger.error(msg4)

        f = open(file)
        for line in f:
            if msg1 in line:
                self.assertTrue("INFO" in line)
            if msg2 in line:
                self.assertTrue("WARNING" in line)
            if msg3 in line:
                self.assertTrue("INFO" in line)
            if msg4 in line:
                self.assertTrue("ERROR" in line)


if __name__ == '__main__':
    unittest.main()
