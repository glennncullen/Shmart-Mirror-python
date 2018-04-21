from AWSIoTPythonSDK.exception.AWSIoTExceptions import *
from app.mqtt import connect
import json

def publish(client, path, publish_json, lock, qos=1):
	lock.acquire()
	try:
		client.publish(path, json.dumps(publish_json), QoS=qos)
	except IOError:
		print "IOError on ", path
	except publishTimeoutException as error:
		print "Publish Timeout: %s" % error
		client = connect.get_client()
		client.publish(path, json.dumps(publish_json), QoS=qos)
	finally:
		lock.release()
