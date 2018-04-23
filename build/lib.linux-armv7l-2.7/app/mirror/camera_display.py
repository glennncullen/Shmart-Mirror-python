from Tkinter import *
from PIL import Image
from PIL import ImageTk
from google.cloud import storage
import os

class CameraFeed(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/shmart_mirror/app/mirror/credentials/Shmart Mirror-b8c85a15ed82.json"
		storage_client = storage.Client()
		bucket_name = 'tesht_bucket_04'
		bucket = storage_client.get_bucket(bucket_name)
		
		blob = bucket.blob("selected_YES.jpg")
		
		with open('assets/selected_YES.jpg', 'rb') as my_file:
			blob.upload_from_file(my_file)
		
		download_blob = bucket.get_blob("selected_YES.jpg")
		print type(download_blob.download_as_string())
