from Tkinter import *
import locale
import feedparser
from PIL import Image
from PIL import ImageTk


class Newsfeed(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		
		self.configure(background='black')
		self.selected_category = 0
		self.category_names = [
						'World', 
						'Ireland', 
						'Business', 
						'Technology', 
						'Entertainment',
						'Sport',
						'Science',
						'Health'
						]
		self.category_url = {
			'World' : "WORLD.en_ie/World",
			'Ireland' : "NATION.en_ie/Ireland",
			'Business' : "BUSINESS.en_ie/Business",
			'Technology' : "TECHNOLOGY.en_ie/Technology",
			'Entertainment' : "ENTERTAINMENT.en_ie/Entertainment",
			'Sport' : "SPORTS.en_ie/Sport",
			'Science' : "SCIENCE.en_ie/Science",
			'Health' : "HEALTH.en_ie/Health"
		}
		self.selected_YES_img = Image.open("assets/selected_YES.jpg")
		self.selected_YES_img = self.selected_YES_img.resize((16, 16))
		self.selected_YES_img = self.selected_YES_img.convert('RGB')
		self.selected_YES = ImageTk.PhotoImage(self.selected_YES_img)
		
		self.selected_NO_img = Image.open("assets/selected_NO.jpg")
		self.selected_NO_img = self.selected_NO_img.resize((16, 16))
		self.selected_NO_img = self.selected_NO_img.convert('RGB')
		self.selected_NO = ImageTk.PhotoImage(self.selected_NO_img)
		
		self.title_lbl = Label(self, text="News", font=('Arial', 48), fg="white", bg="black")
		self.title_lbl.pack(side=TOP, anchor=NW)
		
		self.rss_feeds = {}
		for category in self.category_names:
			url = "https://news.google.com/news/rss/headlines/section/topic/%s?ned=en_ie&gl=IE&hl=en-IE" % self.category_url[category]
			self.rss_feeds[category] = feedparser.parse(url)
		
		self.categories_frame = Frame(self, bg='black')
		self.categories_frame.pack(side=TOP, anchor=NE)
		self.build_categories()
		
		self.headlines_frame = Frame(self, bg='black')
		self.headlines_frame.pack(side=BOTTOM, anchor=SW)
		self.build_headlines()
	
	# move up or down through categories
	def change_category(self, direction):
		self.categories_frame.winfo_children()[self.selected_category].icon_lbl.configure(image=self.selected_NO)
		self.categories_frame.winfo_children()[self.selected_category].icon_lbl.image = self.selected_NO
		self.selected_category += direction
		if self.selected_category < 0:
			self.selected_category = 7
		elif self.selected_category > 7:
			self.selected_category = 0
		self.categories_frame.winfo_children()[self.selected_category].icon_lbl.configure(image=self.selected_YES)
		self.categories_frame.winfo_children()[self.selected_category].icon_lbl.image = self.selected_YES
		self.build_headlines()
	
	# build Category frames
	def build_categories(self):		
		for category in self.category_names:
			line = Category(self.categories_frame, category, self.category_names[self.selected_category])
			line.pack(side=TOP, anchor=W)
	
	# build Headline frames
	def build_headlines(self):
		try:
			# clear previous headlines
			for line in self.headlines_frame.winfo_children():
				line.destroy()
			
			title = Label(self.headlines_frame, text=self.category_names[self.selected_category], font=('Arial', 28), fg="white", bg="black")
			title.pack(side=TOP, anchor=W)
			
			# limit length of headline to 80 characters
			for article in self.rss_feeds[self.category_names[self.selected_category]].entries:
				if len(article.title) < 100:
					line = Headline(self.headlines_frame, article.title)
					line.pack(side=TOP, anchor=W)
				if len(self.headlines_frame.winfo_children()) > 4:
					break
			
		except Exception as error:
			print "Error: %s. Unable to retrieve news." % error


# small frame for displaying categories
# if category being built is selected
# a white dot is added beside the category name
class Category(Frame):
	def __init__(self, parent, category_name, selected_category_name):
		Frame.__init__(self, parent, bg='black')
		
		if category_name == selected_category_name:
			icon = Image.open("assets/selected_YES.jpg")
		else:
			icon = Image.open("assets/selected_NO.jpg")
		
		icon = icon.resize((16, 16))
		icon = icon.convert('RGB')
		pic = ImageTk.PhotoImage(icon)
		self.icon_lbl = Label(self, bg='black', image=pic)
		self.icon_lbl.image = pic
		self.icon_lbl.pack(side=LEFT, anchor=CENTER)
		
		self.category_lbl = Label(self, text=category_name, font=('Arial', 18), fg='white', bg='black')
		self.category_lbl.pack(side=LEFT, anchor=CENTER)


# small frame for displaying the headlines
class Headline(Frame):
	def __init__(self, parent, headline):
		Frame.__init__(self, parent, bg='black')
		
		icon = Image.open("assets/newspaper_symbol.jpg")
		icon = icon.resize((16, 16))
		icon = icon.convert('RGB')
		pic = ImageTk.PhotoImage(icon)
		
		self.icon_lbl = Label(self, bg='black', image=pic)
		self.icon_lbl.image = pic
		self.icon_lbl.pack(side=LEFT, anchor=CENTER)
		
		self.headline_lbl = Label(self, text=headline, font=('Arial', 14), fg='white', bg="black")
		self.headline_lbl.pack(side=LEFT, anchor=N)
