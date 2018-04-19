from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import uuid

def get_client():
	# set up AWS IoT MQTT
	myMQTTClient = AWSIoTMQTTClient(str(uuid.uuid1())) # Add client ID
	myMQTTClient.configureEndpoint("a3oazwlb9g85vu.iot.us-east-2.amazonaws.com", 8883) # endpoint
	myMQTTClient.configureCredentials("/home/pi/shmart_mirror/app/mqtt/credentials/root.pem", "/home/pi/shmart_mirror/app/mqtt/credentials/cdbd424344-private.pem.key", "/home/pi/shmart_mirror/app/mqtt/credentials/cdbd424344-certificate.pem.crt") # Add paths (CA, private key, cert)
	myMQTTClient.configureOfflinePublishQueueing(-1) # Infinite offline publish queueing
	myMQTTClient.configureDrainingFrequency(2) # Draining: 2 Hz
	myMQTTClient.configureConnectDisconnectTimeout(10) # Disconnect at 10 seconds
	myMQTTClient.configureMQTTOperationTimeout(5) #Operation timeout 5 seconds
	# connect to AWS IoT MQTT
	try:
		myMQTTClient.connect()
		return myMQTTClient
	except Error:
		print("unable to connect MQTT")
