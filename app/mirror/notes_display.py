from Tkinter import *
from PIL import Image
from PIL import ImageTk
from firebase import firebase

class NotesFeed(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		
