from app.mqtt import publish, connect, subscribe
from app.mirror.weather_display import WeatherFeed
from app.mirror.news_display import NewsFeed
from app.mirror.notes_display import NotesFeed
from app.mirror.welcome_display import WelcomeFeed
from app.mirror.camera_display import CameraFeed
from threading import _RLock
import traceback
import time
import json
import flicklib
from Tkinter import *
from ttk import *

# variables for lock and client for symmetry throughout app
lock = _RLock()
mqtt_client = connect.get_client()
# array of displays
displays = []
# initialise ready variable to False until system is ready
ready = False

# callback for /iotappdev/pi/auth/
#  - makes sure current display is welcome_display
#  - checks if received auth number is correct
#  	* if correct call change display method with 0 direction and publish authorised to AWS
#   * if not correct publish unauthorised to AWS
#  - asyn publishing used so that callback does not continually publish
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
			publish.publish_async(
				mqtt_client, 
				'/iotappdev/android/auth/', 
				response_json, 
				lock
				)
			time.sleep(0.1)
			publish.publish_async(
				mqtt_client, 
				"/iotappdev/display/", 
				{'display' : displays[selected_display].__class__.__name__}, 
				lock
				)
	except ValueError:
		print "Unable to decode json for auth_callback \n\t incoming message: ", message.payload

# callback for /iotappdev/pi/notes/new/
#  - if json at 'new' is true and display is notes_display, 
#    call get_new_notes function on display
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

# callback for /iotappdev/logout/
def logout_callback(client, userdata, message):
	try:
		json_message = json.loads(message.payload)
		#~ print json_message
		if(json_message["logout"]):
			logout()
	except ValueError:
		print "Unable to decode json for logout_callback \n\t incoming message", messsage.payload

# subscribe to relevant topics and set appropriate callbacks
subscribe.subscribe_to(mqtt_client, "/iotappdev/pi/auth/", auth_callback)
subscribe.subscribe_to(mqtt_client, "/iotappdev/pi/notes/new/", new_notes_callback)
subscribe.subscribe_to(mqtt_client, "/iotappdev/logout/", logout_callback)

# function to change display
#  - remove current display from main frame
#  - if current display is WelcomeFeed
#   * destroy welcome display and remove from displays array
#  -  add direction amount to selected_display
#  - if selected_display is less that 0 or greater
#    thank length of displays array, keep within bounds
#  - if next display is WeatherFeed
#   * pack differently to main frame
#  - else
#   * pack other displays the same way
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

# function to handle logout event
#  - if on welcome_display do nothing
#  - set ready to False
#  - remove current display
#  - add progress bar and start
#  - for each display, call the update function
#  - create new instance of WelcomeFeed and insert at 0 position of displays
#  - set selected_display to 0
#  - stop progress bar and remove from main frame
#  - show Welcome screen
#  - set ready to True
def logout():
	if isinstance(displays[selected_display], WelcomeFeed):
		return
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



# function to handle flick hat double tap gesture
#  - if ready is False do nothing
#  - 'position is not None' indicates a double tap event
#  - call .double_tap on selected_display
@flicklib.double_tap()
def doubletap(position):
	if not ready:
		return
	if position is not None:
		displays[selected_display].double_tap(mqtt_client, lock, ready)


# funtion to handle flick hat flick gesture
#  - if ready is False do nothing
#  - indicate direction in short variable with first letter from start and finish
#  - if North to South 'ns'
#   * call change_vertical_direction on selected display with direction of 1
#  - if South to North 'sn'
#   * call change_vertical_direction on selected display with direction of -1
#  - if West to East 'we'
#   * if selected_display is WelcomeFeed then do nothing
#   * call change display function with direction of 1
#   * publish display now in focus
#  - if East to West 'ew'
#   * if selected_display is WelcomeFeed then do nothing
#   * call change display function with direction of -1
#   * publish display now in focus
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
			publish.publish(
				mqtt_client, 
				"/iotappdev/display/", 
				{'display' : displays[selected_display].__class__.__name__}, 
				lock
				)
			displays[selected_display].on_focus(mqtt_client, lock)
	elif flick_direction == 'ew':
		if not isinstance(displays[selected_display], WelcomeFeed):
			change_display(-1)
			publish.publish(
				mqtt_client, 
				"/iotappdev/display/", 
				{'display' : displays[selected_display].__class__.__name__}, 
				lock
				)
			displays[selected_display].on_focus(mqtt_client, lock)

# function to handler flick hat airwheel gesture
#  - if ready is False do nothing
#  - create a value using the delta from flick library
#  - if value goes above 7.5
#   * reset amount and some_value to 0
#   * call airwheel function on selected display with direction of 1
#  - if value goes below 7.5
#   * reset amount and some_value to 0
#   * call airwheel function on selected display with direction of -1
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
# create gui instance of TK
# set background to black
# don't show cursor on gui
# initialise Style object for progress bar
# create instance of WelcomeFeed and append to dispalys array
# create instance of NotesFeed and append to dispalys array
# create instance of NewsFeed and append to dispalys array
# create instance of WeatherFeed and append to dispalys array
# create instance of CameraFeed and append to dispalys array
# show display in position 0
# publish current display to AWS
# set ready variable to True
# define call back functionality for button binds
# bind Shift-Up to making gui fullscreen
# bind Escape to making gui not fullscreen
# set on_closing function for when gui window is exited
# start main loop
gui = Tk()
gui.configure(background='black')
gui.config(cursor="none")

progress_style = Style()
progress_style.theme_use('clam')
progress_style.configure(
	"white.Horizontal.TProgressbar", 
	foregound='black', 
	background='black', 
	throughcolor='black'
	)
progress = Progressbar(
	gui, 
	style="white gr.Horizontal.TProgressbar", 
	orient=HORIZONTAL, 
	length=gui.winfo_screenwidth(), 
	mode='determinate'
	)

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
print 'Starting CameraFeed'
displays.append(CameraFeed(gui))
print 'CameraFeed started'

displays[selected_display].pack(fill=BOTH, expand=YES, padx=40, pady=40)

publish.publish(
	mqtt_client, 
	"/iotappdev/display/", 
	{'display' : displays[selected_display].__class__.__name__}, 
	lock
	)

ready = True

# function to set gui to fullscreen
def enter_fullscreen(event=None):
	gui.attributes("-fullscreen", True)

# function to remove fullscreen
def close_fullscreen(event=None):
	gui.attributes("-fullscreen", False)

# function to handle gui window being closed
#  - destroy gui
#  - publish logout to AWS
#  - exit the system
def on_closing(event=None):
	gui.destroy()
	publish.publish_async(
		mqtt_client, 
		"/iotappdev/logout/", 
		{"logout": 1}, 
		lock
		)
	sys.exit

gui.bind('<Shift-Up>', enter_fullscreen)
gui.bind('<Escape>', close_fullscreen)

gui.protocol("WM_DELETE_WINDOW", on_closing)
#~ gui.attributes("-fullscreen", True)
gui.mainloop()
