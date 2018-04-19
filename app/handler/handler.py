from threading import _RLock
import app.mqtt.connect as connect


#~ class Singleton(object):
	#~ _instance = None
	
	#~ def __new__(cls, *args, **kwargs):
		#~ if cls._instance is None:
			#~ cls._instance = object.__new__(cls, *args, **kwargs)
		#~ return cls._instance



class Handler(object):

	def __init__(self):
		self.lock = _RLock()
		self.mqtt_client = connect.get_client(self.mqtt_client)


	def client(self):
		self.mqtt_client = connect.get_client(self.mqtt_client)
		return self.mqtt_client
