from app.mqtt import publish, connect, subscribe
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

def publish_callback():
	publish.publish(client, "/iotappdev/test/", test_json, lock)

# GUI 
gui = Tk()

gui.configure(background='black')


publish_button = Button(gui, text="Publish", command=publish_callback)
publish_button.pack()

def enter_fullscreen(event=None):
	gui.attributes("-fullscreen", True)

def close_fullscreen(event=None):
	gui.attributes("-fullscreen", False)

gui.bind('<Shift-Up>', enter_fullscreen)
gui.bind('<Escape>', close_fullscreen)

gui.mainloop()
