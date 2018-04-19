from Tkinter import *
import locale
import feedparser

class Newsfeed(Frame):
	def __init__(self, parent, locale):
		Frame.__init__(self, parent, *args, **kwargs)
		self.configure(background='black')
		self.title_lbl = Label(self, text="News", font=('Arial', medium_text_size), fg="white", bg="black")
		self.title_lbl.pack(side=TOP, anchor=W)
		
