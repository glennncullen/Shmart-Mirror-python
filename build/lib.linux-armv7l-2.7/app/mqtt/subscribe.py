
def subscribe_to(client, path, callback, qos=1):
	if client.subscribe(path, qos, callback):
		print "Subscribed to ", path
