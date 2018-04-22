from Tkinter import *
from PIL import Image
from PIL import ImageTk
from firebase import firebase
from google.cloud import storage
import os

class NotesFeed(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		
		firebase_db = firebase.FirebaseApplication('https://shmart-mirror.firebaseio.com/', None)
		
		print firebase_db.post('/notes', 'Is this real life?')
		
		print firebase_db.get('/notes', None)
		
		#~ firebase_img_db = firebase.FirebaseApplication('gs://shmart-mirror.appspot.com', None)
		
		icon = Image.open("assets/selected_NO.jpg")
		pic = ImageTk.PhotoImage(icon)
		
		os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/shmart_mirror/app/mirror/credentials/Shmart Mirror-b8c85a15ed82.json"
		storage_client = storage.Client()
		bucket_name = 'tesht_bucket_04'
		bucket = storage_client.get_bucket(bucket_name)
		
		blob = bucket.get_blob("selected_YES.jpg")
		
		with open('assets/selected_YES.jpg', 'rb') as my_file:
			blob.upload_from_file(my_file)
		
		download_blob = bucket.get_blob("selected_YES.jpg")
		print type(download_blob.download_as_string())
