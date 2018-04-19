import json

def publish(client, path, publish_json, lock, qos=1):
	lock.acquire()
	try:
		client.publish(path, json.dumps(publish_json), QoS=qos)
	except IOError:
		print "IOError on ", path
	finally:
		lock.release()
