import traceback
from app.mqtt import publish
from Tkinter import *
from PIL import Image
from PIL import ImageTk
from google.cloud import storage
import os
import time
import uuid

from picamera import PiCamera

class CameraFeed(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		
		self.configure(background='black')
		
		# show os where to find credentials
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/shmart_mirror/app/mirror/credentials/Shmart Mirror-b8c85a15ed82.json"
		# initialise google cloud storage client
		storage_client = storage.Client()
		# gain access to relevant part of database
		bucket_name = 'shmart-mirror.appspot.com'
		self.bucket = storage_client.get_bucket(bucket_name)
		
		# initialise piCamera and set how long the countdown timer is
		self.camera = PiCamera()
		self.countdown_timer = 3
		
		# child frame for instructions
		self.camera_frame = Frame(self, bg='black')
		self.camera_frame.pack(side=BOTTOM)
		
		# build frame for camera instructions
		self.build_camera_display()
	
	# instructional frame
	def build_camera_display(self):
		line = Instruction(self.camera_frame, "Double Tap To Take A Snap!!!")
		line.pack(side=LEFT, anchor=E)
	
	# do nothing on focus
	def on_focus(self, *args):
		return
	
	# do nothing on vertical flick hat gesture
	def change_vertical_focus(self, *args):
		return
	
	# on double tap felick hat gesture:
	#  - set ready variable in main.py to False
	#  - create unique picture name
	#  - countdown by updating the child frame with the numbers in the countdown_timer
	#  - capture image and store in /camera_images/
	#  - create 'blob' in cloud storage using pic_name
	#  - upload file to blob from /camera_images/
	#  - delete image from /camera_images/
	#  - reset instructions, countdown_timer and ready variable
	def double_tap(self, *args):
		args[2] = False
		pic_name = str(uuid.uuid4().hex) + ".jpg"
		while self.countdown_timer != 0:
			self.camera_frame.winfo_children()[0].instruction_lbl.config(text=self.countdown_timer)
			self.countdown_timer -= 1
			time.sleep(1)
		self.camera_frame.winfo_children()[0].instruction_lbl.config(text="Cheeeeeeeese!!")
		self.camera.capture('camera_images/%s' % pic_name)
		blob = self.bucket.blob(pic_name)
		with open('camera_images/%s' % pic_name) as my_pic:
			blob.upload_from_file(my_pic)
		publish.publish(args[0], "/iotappdev/android/camera/newpic/", {"pic_name" : pic_name}, args[1])
		os.remove('camera_images/%s' % pic_name)
		self.camera_frame.winfo_children()[0].instruction_lbl.config(text="Double Tap To Take A Snap!!!")
		self.countdown_timer = 3
		args[2] = True
	
	# do nothing on airwheel flick hat gesture
	def airwheel(self, *args):
		return
	
	# do nothing on update
	def update(self):
		return

# small frame for instructions
class Instruction(Frame):
	def __init__(self, parent, instruction):
		Frame.__init__(self, parent, bg='black')
		
		self.instruction_lbl = Label(self, text=instruction, font=('Arial', 30), fg='white', bg="black")
		self.instruction_lbl.pack(side=LEFT, anchor=W, padx=10)
