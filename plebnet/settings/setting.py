from configparser import ConfigParser

class Settings(object):
 	def __init__(self,filename):
		self.settings = ConfigParser()
		self.filename = filename

    def load(self):
#		if not os.path.exists(self.filename):
#			logger.log("Settings","load","file not existing")
#			return False
		files = self.settings.read(self.filename,encoding='utf-8')
		return len(files)>0

	def get(self,section,key):
		return self.settings.get(section,key)

	def set(self,section,key,value):
		if not self.settings.has_section(section):
			self.settings.add_section(section)
		self.settings.set(section,key,value)