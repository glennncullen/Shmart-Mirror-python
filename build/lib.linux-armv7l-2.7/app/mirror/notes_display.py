import traceback
from Tkinter import *
from PIL import Image
from PIL import ImageTk
from firebase import firebase
from google.cloud import storage
import os

class NotesFeed(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		
		self.configure(background='black')
		
		# initialist connection to firebase
		self.firebase_db = firebase.FirebaseApplication('https://shmart-mirror.firebaseio.com/', None)
		self.notes = self.firebase_db.get("", None)
		self.selected_note = 1
		
		# image for selected note
		self.selected_YES_img = Image.open("assets/selected_YES.jpg")
		self.selected_YES_img = self.selected_YES_img.resize((16, 16))
		self.selected_YES_img = self.selected_YES_img.convert('RGB')
		self.selected_YES = ImageTk.PhotoImage(self.selected_YES_img)
		
		# image for not selected note
		self.selected_NO_img = Image.open("assets/selected_NO.jpg")
		self.selected_NO_img = self.selected_NO_img.resize((16, 16))
		self.selected_NO_img = self.selected_NO_img.convert('RGB')
		self.selected_NO = ImageTk.PhotoImage(self.selected_NO_img)
		
		# child frame to contain notes
		self.notes_frame = Frame(self, bg='black')
		self.notes_frame.pack(side=BOTTOM, anchor=W)
		self.build_notes()
	
	# when flick receives vertical gesture
	# move up or down through notes
	def change_vertical_focus(self, direction, *args):
		if self.notes is None:
			return
		self.notes_frame.winfo_children()[self.selected_note].icon_lbl.configure(image=self.selected_NO)
		self.notes_frame.winfo_children()[self.selected_note].icon_lbl.image = self.selected_NO
		#~ print self.selected_note
		self.selected_note += direction
		if self.selected_note < 1:
			self.selected_note = len(self.notes) 
		elif self.selected_note > len(self.notes):
			self.selected_note = 1
		#~ print self.selected_note
		self.notes_frame.winfo_children()[self.selected_note].icon_lbl.configure(image=self.selected_YES)
		self.notes_frame.winfo_children()[self.selected_note].icon_lbl.image = self.selected_YES
	
	# delete selected note from firebase on doubletap
	def double_tap(self, *args):
		with args[1]:
			self.firebase_db.delete('', self.notes.keys()[self.selected_note - 1])
			self.notes = self.firebase_db.get('', None)
			self.selected_note = 1
			self.build_notes()
	
	# when flick hat recives airwheel gesture
	# move selected note up or down
	def airwheel(self, direction, *args):
		self.change_vertical_focus(direction)
	
	# get any new notes from firebase
	def get_new_notes(self):
		self.notes = self.firebase_db.get('', None)
		self.selected_note = 1
		self.build_notes()
	
	# destroy any previous notes and build new 
	# notes into frames
	def build_notes(self):
		for line in self.notes_frame.winfo_children():
			line.destroy()
		self.title_lbl = Label(self.notes_frame, text="Notes", font=('Arial', 28), fg="white", bg="black")
		self.title_lbl.pack(side=TOP, anchor=NW, pady=10)
		if self.notes is None:
			return
		for note in self.notes:
			line = Note(self.notes_frame, self.notes[note], (self.notes.values()[0] == self.notes[note]))
			line.pack(side=TOP, anchor=W)
	
	# when display is updated, check for new notes
	def update(self):
		self.get_new_notes()
	
	# do nothing when display is in focus
	def on_focus(self, *args):
		return

# child frame for individual notes
# if note is selected, add selceted_YES image
# beside the note
class Note(Frame):
	def __init__(self, parent, note, selected):
		Frame.__init__(self, parent, bg='black')
		
		if selected:
			icon = Image.open("assets/selected_YES.jpg")
		else:
			icon = Image.open("assets/selected_NO.jpg")
		
		icon = icon.resize((16, 16))
		icon = icon.convert('RGB')
		pic = ImageTk.PhotoImage(icon)
		
		self.icon_lbl = Label(self, bg='black', image=pic)
		self.icon_lbl.image = pic
		self.icon_lbl.pack(side=LEFT, anchor=CENTER, padx=10)
		
		self.note_lbl = Label(self, text=note, font=('Arial', 20), fg='white', bg="black")
		self.note_lbl.pack(side=LEFT, anchor=N, fill=X)
