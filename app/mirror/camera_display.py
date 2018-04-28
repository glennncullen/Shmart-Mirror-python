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
		
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/shmart_mirror/app/mirror/credentials/Shmart Mirror-b8c85a15ed82.json"
		storage_client = storage.Client()
		bucket_name = 'shmart-mirror.appspot.com'
		self.bucket = storage_client.get_bucket(bucket_name)
		
		self.camera = PiCamera()
		self.countdown_timer = 3
		
		self.camera_frame = Frame(self, bg='black')
		self.camera_frame.pack(side=BOTTOM)
		
		self.build_camera_display()
	
	
	def build_camera_display(self):
		line = Instruction(self.camera_frame, "Double Tap To Take A Snap!!!")
		line.pack(side=LEFT, anchor=E)
	
	
	def on_focus(self, *args):
		return
	
	def change_vertical_focus(self, *args):
		return
	
	def double_tap(self, *args):
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
	
	def airwheel(self, *args):
		return
	
	def update(self):
		return


class Instruction(Frame):
	def __init__(self, parent, instruction):
		Frame.__init__(self, parent, bg='black')
		
		self.instruction_lbl = Label(self, text=instruction, font=('Arial', 30), fg='white', bg="black")
		self.instruction_lbl.pack(side=LEFT, anchor=W, padx=10)
