from configparser import ConfigParser
from appdirs import *


class Settings(object):
	def __init__(self, filename):
		self.settings = ConfigParser()
		self.filename = filename

	def load(self, filename=None):
		if not filename:
			filename = self.filename

		if not os.path.exists(filename):
			print("Config file: '%s' not found" % filename)
			return False
		files = self.settings.read(filename, encoding='utf-8')
		return len(files) > 0

	def get(self, section, key):
		return self.settings.get(section, key)

	def set(self, section, key, value):
		if not self.settings.has_section(section):
			self.settings.add_section(section)
		self.settings.set(section, key, value)
