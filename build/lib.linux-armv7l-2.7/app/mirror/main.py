from app.mqtt import publish, connect, subscribe
from app.mirror.news_display import Newsfeed
from threading import _RLock
import time
import json
import flicklib

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

airwheeltxt = ''
some_value = 0

@flicklib.airwheel()
def spinny(delta):
	global some_value
	global airwheeltxt
	some_value += delta
	if some_value < -5000:
		some_value = -5000
	if some_value > 5000:
		some_value = 5000
	airwheeltxt = str(some_value/100)
	amount = some_value/100
	if amount > 10:
		amount, some_value = 0, 0
		move_category_down()
	elif amount < -10:
		amount, some_value = 0, 0
		move_category_up()

# GUI 
gui = Tk()

gui.configure(background='black')

news_display = Newsfeed(gui)
news_display.pack(fill=BOTH, expand=YES, padx=80, pady=20)

#~ test_lbl = Label(gui, text="heya", font=('Arial', 20), fg='white', bg='black')
#~ test_lbl.pack()

def enter_fullscreen(event=None):
	gui.attributes("-fullscreen", True)

def close_fullscreen(event=None):
	gui.attributes("-fullscreen", False)

def move_category_up(event=None):
	news_display.change_category(-1)

def move_category_down(event=None):
	news_display.change_category(1)

gui.bind('<Shift-Up>', enter_fullscreen)
gui.bind('<Escape>', close_fullscreen)
gui.bind('<Up>', move_category_up)
gui.bind('<Down>', move_category_down)


gui.mainloop()
