from app.mqtt import publish, connect, subscribe
from app.mirror.weather_display import WeatherFeed
from app.mirror.news_display import NewsFeed
from app.mirror.notes_display import NotesFeed
from threading import _RLock
import time
import json
import flicklib

from Tkinter import *

lock = _RLock()
client = connect.get_client()
displays = []
ready = False

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

selected_display = 0
def change_display(direction):
	global selected_display
	displays[selected_display].pack_forget()
	selected_display += direction
	if selected_display < 0:
		selected_display = len(displays) - 1
	elif selected_display > len(displays) - 1:
		selected_display = 0
	if isinstance(displays[selected_display], WeatherFeed):
		displays[selected_display].pack(anchor=NE, expand=YES, padx=40, pady=40)
	else:
		displays[selected_display].pack(fill=BOTH, expand=YES, padx=40, pady=40)

@flicklib.double_tap()
def doubletap(position):
	if not ready:
		return
	if position is not None:
		displays[selected_display].double_tap(client, lock)

@flicklib.flick()
def flick(start, finish):
	if not ready:
		return
	global selected_display
	flick_direction = '' + start[0] + finish[0]
	if flick_direction == 'ns':
		displays[selected_display].change_vertical_focus(1, client, lock)
	elif flick_direction == 'sn':
		displays[selected_display].change_vertical_focus(-1, client, lock)
	elif flick_direction == 'we':
		change_display(1)
	elif flick_direction == 'ew':
		change_display(-1)


some_value = 0
@flicklib.airwheel()
def spinny(delta):
	if not ready:
		return
	global some_value
	some_value += delta
	amount = some_value/100
	if amount > 7.5:
		amount, some_value = 0, 0
		displays[selected_display].airwheel(1, client, lock)
	elif amount < -7.5:
		amount, some_value = 0, 0
		displays[selected_display].airwheel(-1, client, lock)

# GUI 
gui = Tk()
gui.configure(background='black')
gui.config(cursor="none")

print 'starting NotesFeed'
displays.append(NotesFeed(gui))
print 'NotesFeed started'
print 'starting NewsFeed'
displays.append(NewsFeed(gui))
print 'NewsFeed started'
print 'starting WeatherFeed'
displays.append(WeatherFeed(gui))
print 'WeatherFeed started'
displays[selected_display].pack(fill=BOTH, expand=YES, padx=40, pady=40)

ready = True

def enter_fullscreen(event=None):
	gui.attributes("-fullscreen", True)

def close_fullscreen(event=None):
	gui.attributes("-fullscreen", False)


def change_display_left(event=None):
	change_display(-1)

def change_display_right(event=None):
	change_display(1)

gui.bind('<Shift-Up>', enter_fullscreen)
gui.bind('<Escape>', close_fullscreen)
#~ gui.bind('<Up>', move_note_up)
#~ gui.bind('<Down>', move_note_down)
gui.bind('<Left>', change_display_left)
gui.bind('<Right>', change_display_right)

def on_closing(event=None):
	gui.destroy()
	sys.exit

gui.protocol("WM_DELETE_WINDOW", on_closing)
gui.mainloop()
