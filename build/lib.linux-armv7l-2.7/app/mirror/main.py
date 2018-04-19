import app.mqtt.publish as publish
import app.mqtt.connect as connect
import app.mqtt.subscribe as subscribe
from app.handler.handler import Handler
from threading import _RLock
import time
import json

from Tkinter import *

lock = _RLock()
client = connect.get_client()

def testCallback(client, userdata, message):
	print(message.payload)
	try:
		json_message = json.loads(message.payload)
		print(json_message["testField"])
	except ValueError:
		print "Unable to decode json for testCallBack \n\t incoming message: ", message.payload

test_json = {}
test_json["testField"] = "testing this"

subscribe.subscribe_to(client, "/iotappdev/test/", testCallback)


#~ while True:
	#~ try:
		#~ time.sleep(2)
		#~ publish.publish(client, "/iotappdev/test/", test_json, lock)
	#~ except KeyboardInterrupt:
		#~ break

def publish_callback():
	publish.publish(client, "/iotappdev/test/", test_json, lock)

# GUI 
root = Tk()
label = Label(root, text="press to test")
label.pack()
button = Button(root, text="Publish", command=publish_callback)
button.pack()
root.mainloop()
