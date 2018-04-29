import traceback
from app.mqtt import publish
from Tkinter import *
import random

class WelcomeFeed(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		
		self.configure(background='black')
		
		# set random 6 digit number for authorisation
		self.auth_num = random.randint(100000, 999999)
		
		# child frame to store auth numbers
		self.welcome_frame = Frame(self, bg='black')
		self.welcome_frame.pack(side=BOTTOM)
		
		# build frames for welcome frame
		self.build_welcome()
	
	# do nothing on vertical flick hat gesture
	def change_vertical_focus(self, *args):
		return
	
	# do nothing on double tap flick hat gesture
	def double_tap(self, *args):
		return
	
	# do nothing on airwheel flick hat gesture
	def airwheel(self, *args):
		return
	
	# do nothing on update
	def update(self):
		return
	
	# create individual frames for authorisation number
	def build_welcome(self):
		for number in str(self.auth_num):
			line = Number(self.welcome_frame, number)
			line.pack(side=LEFT, anchor=W)
	
	# check if correct authorisation number has been received
	def check_auth(self, num):
		if int(num) == self.auth_num:
			return True
		else:
			return False
	
	# publish authorisation to iotappdev
	def authorised(self, client, lock):
		response_json = {}
		response_json["auth"] = 'authorised'
		publish.publish_async(client, '/iotappdev/android/auth/', response_json, lock)


# child frame for individual numbers
class Number(Frame):
	def __init__(self, parent, number):
		Frame.__init__(self, parent, bg='black')
		
		self.number_lbl = Label(self, text=number, font=('Arial', 30), fg='white', bg="black")
		self.number_lbl.pack(side=LEFT, anchor=W, padx=10)
