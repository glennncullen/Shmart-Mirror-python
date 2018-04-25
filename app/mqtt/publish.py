from AWSIoTPythonSDK.exception.AWSIoTExceptions import *
from app.mqtt import connect
import json
import logging
import traceback

def publish(client, path, publish_json, lock, qos=1):
	logging.basicConfig()
	lock.acquire()
	try:
		#~ print "publishing: ", publish_json, " to ", path
		client.publish(path, json.dumps(publish_json), QoS=qos)
	except IOError:
		print "IOError on ", path
	except publishTimeoutException as error:
		print "Publish Timeout Exception: %s" % error
	finally:
		lock.release()

def publish_async(client, path, publish_json, lock, qos=1):
	logging.basicConfig()
	lock.acquire()
	try:
		#~ print "async publishing: ", publish_json, " to ", path
		client.publishAsync(path, json.dumps(publish_json), QoS=qos)
	except IOError:
		print "IOError on ", path
	except publishTimeoutException as error:
		print "Async Publish Timeout Exception: %s" % error
	finally:
		lock.release()
