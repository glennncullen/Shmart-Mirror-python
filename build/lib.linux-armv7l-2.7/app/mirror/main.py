from app.mqtt import publish, connect, subscribe
from app.mirror.weather_display import WeatherFeed
from app.mirror.news_display import NewsFeed
from app.mirror.notes_display import NotesFeed
from app.mirror.welcome_display import WelcomeFeed
from threading import _RLock
import time
import json
import flicklib
from Tkinter import *
from ttk import *

lock = _RLock()
mqtt_client = connect.get_client()
displays = []
ready = False

def news_article_link_callback(client, userdata, message):
	try:
		json_message = json.loads(message.payload)
		#~ print(json_message["link"])
	except ValueError:
		print "Unable to decode json for testCallBack \n\t incoming message: ", message.payload

def weather_day_callback(client, userdata, message):
	try:
		json_message = json.loads(message.payload)
		#~ print json_message
	except ValueError:
		print "Unable to decode json for testCallBack \n\t incoming message: ", message.payload


def display_callback(client, userdata, message):
	try:
		json_message = json.loads(message.payload)
		#~ print "display_callback: %s" % json_message
	except ValueError:
		print "Unable to decode json for displayCallBack \n\t incoming message: ", message.payload

def auth_callback(client, userdata, message):
	try:
		json_message = json.loads(message.payload)
		#~ print json_message
		if isinstance(displays[selected_display], WelcomeFeed):
			response_json = {}
			if displays[selected_display].check_auth(json_message["auth"]):
				response_json["auth"] = 'authorised'
				change_display(0)
			else:
				response_json["auth"] = 'unauthorised'
			publish.publish_async(mqtt_client, '/iotappdev/android/auth/', response_json, lock)
			time.sleep(0.1)
			publish.publish_async(mqtt_client, "/iotappdev/display/", {'display' : displays[selected_display].__class__.__name__}, lock)
	except ValueError:
		print "Unable to decode json for displayCallBack \n\t incoming message: ", message.payload


def new_notes_callback(client, userdata, message):
	try:
		json_message = json.loads(message.payload)
		#~ print json_message
		if(json_message["new"]):
			for display in displays:
				if isinstance(display, NotesFeed):
					display.get_new_notes()
	except ValueError:
		print "Unable to decode json for new_notes_callback \n\t incoming message", messsage.payload
		

def logout_callback(client, userdata, message):
	try:
		json_message = json.loads(message.payload)
		#~ print json_message
		if(json_message["logout"]):
			logout()
	except ValueError:
		print "Unable to decode json for logout_callback \n\t incoming message", messsage.payload

subscribe.subscribe_to(mqtt_client, "/iotappdev/news/article/link/", news_article_link_callback)
subscribe.subscribe_to(mqtt_client, "/iotappdev/weather/day/", weather_day_callback)
subscribe.subscribe_to(mqtt_client, "/iotappdev/display/", display_callback)
subscribe.subscribe_to(mqtt_client, "/iotappdev/pi/auth/", auth_callback)
subscribe.subscribe_to(mqtt_client, "/iotappdev/pi/notes/new/", new_notes_callback)
subscribe.subscribe_to(mqtt_client, "/iotappdev/logout/", logout_callback)


def publish_link():
	link_json = {}
	link_json["link"] = news_display.get_link()
	publish.publish(mqtt_client, "/iotappdev/news/article/link/", link_json, lock)

def publish_current_display():
	publish.publish(mqtt_client, "/iotappdev/display/", {'display' : displays[selected_display].__class__.__name__}, lock)


selected_display = 0
def change_display(direction):
	global selected_display
	displays[selected_display].pack_forget()
	if isinstance(displays[selected_display], WelcomeFeed):
		displays[selected_display].destroy
		displays.remove(displays[selected_display])
	selected_display += direction
	if selected_display < 0:
		selected_display = len(displays) - 1
	elif selected_display > len(displays) - 1:
		selected_display = 0
	if isinstance(displays[selected_display], WeatherFeed):
		displays[selected_display].pack(anchor=NE, expand=YES, padx=40, pady=40)
	else:
		displays[selected_display].pack(fill=BOTH, expand=YES, padx=40, pady=40)

def logout():
	ready = False
	global selected_display
	displays[selected_display].pack_forget()
	progress.pack()
	progress.start()
	for display in displays:
		display.update()
	displays.insert(0, WelcomeFeed(gui))
	selected_display = 0
	progress.stop()
	progress.pack_forget()
	displays[selected_display].pack(fill=BOTH, expand=YES, padx=40, pady=40)
	ready = True

@flicklib.double_tap()
def doubletap(position):
	if not ready:
		return
	if position is not None:
		displays[selected_display].double_tap(mqtt_client, lock)

@flicklib.flick()
def flick(start, finish):
	if not ready:
		return
	global selected_display
	flick_direction = '' + start[0] + finish[0]
	if flick_direction == 'ns':
		displays[selected_display].change_vertical_focus(1, mqtt_client, lock)
	elif flick_direction == 'sn':
		displays[selected_display].change_vertical_focus(-1, mqtt_client, lock)
	elif flick_direction == 'we':
		if not isinstance(displays[selected_display], WelcomeFeed):
			change_display(1)
			publish_current_display()
			displays[selected_display].on_focus(mqtt_client, lock)
	elif flick_direction == 'ew':
		if not isinstance(displays[selected_display], WelcomeFeed):
			change_display(-1)
			publish_current_display()
			displays[selected_display].on_focus(mqtt_client, lock)

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
		displays[selected_display].airwheel(1, mqtt_client, lock)
	elif amount < -7.5:
		amount, some_value = 0, 0
		displays[selected_display].airwheel(-1, mqtt_client, lock)

# GUI 
gui = Tk()
gui.configure(background='black')
gui.config(cursor="none")

progress_style = Style()
progress_style.theme_use('clam')
progress_style.configure("white.Horizontal.TProgressbar", foregound='black', background='black', throughcolor='black')
progress = Progressbar(gui, style="white gr.Horizontal.TProgressbar", orient=HORIZONTAL, length=gui.winfo_screenwidth(), mode='determinate')

print 'starting WelcomeFeed'
displays.append(WelcomeFeed(gui))
print 'WelcomeFeed started'
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
publish_current_display()

ready = True

def enter_fullscreen(event=None):
	gui.attributes("-fullscreen", True)

def close_fullscreen(event=None):
	gui.attributes("-fullscreen", False)


def change_display_left(event=None):
	change_display(-1)
	publish_current_display()

def change_display_right(event=None):
	change_display(1)
	publish_current_display()


gui.bind('<Shift-Up>', enter_fullscreen)
gui.bind('<Escape>', close_fullscreen)
#~ gui.bind('<Up>', move_note_up)
#~ gui.bind('<Down>', move_note_down)
gui.bind('<Left>', change_display_left)
gui.bind('<Right>', change_display_right)
#~ gui.bind('<Return>', send_auth)

def on_closing(event=None):
	gui.destroy()
	publish.publish_async(mqtt_client, "/iotappdev/logout/", {"logout": 1}, lock)
	sys.exit

gui.protocol("WM_DELETE_WINDOW", on_closing)
gui.mainloop()
