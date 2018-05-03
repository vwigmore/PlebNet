from plebnet.settings import setting

class AgentSettings(object):
 	def __init__(self):
		self.filename = "configuration/agent.cfg"
		self.settings = setting.Settings(self.filename)
        self.load()

    def get_uploaded(){
        return self.settings.get("data","uploaded")
    }