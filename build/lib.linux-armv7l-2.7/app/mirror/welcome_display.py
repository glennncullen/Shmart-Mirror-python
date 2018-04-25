from app.mqtt import publish
from Tkinter import *
import random

class WelcomeFeed(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		
		self.configure(background='black')
		
		self.auth_num = random.randint(100000, 999999)
		
		self.welcome_frame = Frame(self, bg='black')
		self.welcome_frame.pack(side=BOTTOM)
	
		self.build_welcome()
	
	def change_vertical_focus(self, *args):
		return
	
	def double_tap(self, *args):
		return
	
	def airwheel(self, *args):
		return
	
	def build_welcome(self):
		for number in str(self.auth_num):
			line = Number(self.welcome_frame, number)
			line.pack(side=LEFT, anchor=W)
	
	def check_auth(self, num):
		if int(num) == self.auth_num:
			return True
		else:
			return False
	
	def authorised(self, client, lock):
		response_json = {}
		response_json["auth"] = 'authorised'
		publish.publish_async(client, '/iotappdev/android/auth/', response_json, lock)

class Number(Frame):
	def __init__(self, parent, number):
		Frame.__init__(self, parent, bg='black')
		
		self.number_lbl = Label(self, text=number, font=('Arial', 30), fg='white', bg="black")
		self.number_lbl.pack(side=LEFT, anchor=W, padx=10)
