from app.mqtt import publish, connect, subscribe
from app.mirror.weather_display import WeatherFeed
from app.mirror.news_display import Newsfeed
from app.mirror.notes_display import NotesFeed
from threading import _RLock
import time
import json
import flicklib

from Tkinter import *

lock = _RLock()
client = connect.get_client()

#~ def testCallback(client, userdata, message):
	#~ print(message.payload)
	#~ try:
		#~ json_message = json.loads(message.payload)
		#~ print(json_message["testField"])
	#~ except ValueError:
		#~ print "Unable to decode json for testCallBack \n\t incoming message: ", message.payload

#~ test_json = {}
#~ test_json["testField"] = "testing this"

#~ subscribe.subscribe_to(client, "/iotappdev/test/", testCallback)

#~ def publish_callback():
	#~ publish.publish(client, "/iotappdev/test/", test_json, lock)


def news_article_link_callback(client, userdata, message):
	try:
		json_message = json.loads(message.payload)
		print(json_message["link"])
	except ValueError:
		print "Unable to decode json for testCallBack \n\t incoming message: ", message.payload

def weather_day_callback(client, userdata, message):
	try:
		json_message = json.loads(message.payload)
		#~ print json_message
	except ValueError:
		print "Unable to decode json for testCallBack \n\t incoming message: ", message.payload

subscribe.subscribe_to(client, "/iotappdev/news/article/link/", news_article_link_callback)
subscribe.subscribe_to(client, "/iotappdev/weather/day/", weather_day_callback)


def publish_link():
	link_json = {}
	link_json["link"] = news_display.get_link()
	publish.publish(client, "/iotappdev/news/article/link/", link_json, lock)

def publish_weather():
	publish.publish(client, "/iotappdev/weather/day/", weather_display.forecast[weather_display.selected_day], lock)


@flicklib.double_tap()
def doubletap(position):
	if position is not None:
		publish_link()

@flicklib.flick()
def flick(start, finish):
	flick_direction = '' + start[0] + finish[0]
	if flick_direction == 'ns':
		#~ news_display.change_headline(1)
		weather_display.change_day(1)
		publish_weather()
	elif flick_direction == 'sn':
		#~ news_display.change_headline(-1)
		weather_display.change_day(-1)
		publish_weather()

some_value = 0
@flicklib.airwheel()
def spinny(delta):
	global some_value
	some_value += delta
	amount = some_value/100
	if amount > 7.5:
		amount, some_value = 0, 0
		#~ news_display.change_category(
		weather_display.change_day(1)
		publish_weather()
	elif amount < -7.5:
		amount, some_value = 0, 0
		#~ news_display.change_category(-1)
		weather_display.change_day(-1)
		publish_weather()

# GUI 
gui = Tk()

gui.configure(background='black')
gui.config(cursor="none")

#~ news_display = Newsfeed(gui)
#~ news_display.pack(fill=BOTH, expand=YES, padx=80, pady=20)

#~ weather_display = WeatherFeed(gui)
#~ weather_display.pack(anchor=NE, expand=YES, padx=40, pady=40)

notes_display = NotesFeed(gui)
notes_display.pack(fill=BOTH, expand=YES, padx=40, pady=40)

#~ test_lbl = Label(gui, text="heya", font=('Arial', 20), fg='white', bg='black')
#~ test_lbl.pack()

def enter_fullscreen(event=None):
	gui.attributes("-fullscreen", True)

def close_fullscreen(event=None):
	gui.attributes("-fullscreen", False)


def move_day_up(event=None):
	notes_display.change_day(-1)

def move_day_down(event=None):
	notes_display.change_day(1)

gui.bind('<Shift-Up>', enter_fullscreen)
gui.bind('<Escape>', close_fullscreen)
gui.bind('<Up>', move_note_up)
gui.bind('<Down>', move_note_down)

def on_closing(event=None):
	gui.destroy()
	sys.exit

gui.protocol("WM_DELETE_WINDOW", on_closing)
gui.mainloop()
