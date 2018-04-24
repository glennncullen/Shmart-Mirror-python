from app.mqtt import publish
from Tkinter import *
import feedparser
from PIL import Image
from PIL import ImageTk


class NewsFeed(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		
		self.selected_headline = 1
		self.current_headlines = {}
		self.headline_titles = []
		
		self.configure(background='black')
		self.selected_category = 1
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
		
		self.newspaper_YES_img = Image.open("assets/newspaper_YES.jpg")
		self.newspaper_YES_img = self.newspaper_YES_img.resize((16, 16))
		self.newspaper_YES_img = self.newspaper_YES_img.convert('RGB')
		self.newspaper_YES = ImageTk.PhotoImage(self.newspaper_YES_img)
		
		self.selected_NO_img = Image.open("assets/selected_NO.jpg")
		self.selected_NO_img = self.selected_NO_img.resize((16, 16))
		self.selected_NO_img = self.selected_NO_img.convert('RGB')
		self.selected_NO = ImageTk.PhotoImage(self.selected_NO_img)
		
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
	
	def change_vertical_focus(self, direction, *args):
		if len(self.headline_titles) is 1:
			return
		self.headlines_frame.winfo_children()[self.selected_headline].icon_lbl.configure(image=self.selected_NO)
		self.headlines_frame.winfo_children()[self.selected_headline].icon_lbl.image = self.selected_NO
		self.selected_headline += direction
		if self.selected_headline < 1:
			self.selected_headline = len(self.headline_titles) - 1
		elif self.selected_headline > len(self.headline_titles) - 1:
			self.selected_headline = 1
		self.headlines_frame.winfo_children()[self.selected_headline].icon_lbl.configure(image=self.newspaper_YES)
		self.headlines_frame.winfo_children()[self.selected_headline].icon_lbl.image = self.newspaper_YES
	
	# move up or down through categories
	def airwheel(self, direction, *args):
		self.categories_frame.winfo_children()[self.selected_category].icon_lbl.configure(image=self.selected_NO)
		self.categories_frame.winfo_children()[self.selected_category].icon_lbl.image = self.selected_NO
		self.selected_category += direction
		if self.selected_category < 1:
			self.selected_category = 8
		elif self.selected_category > 8:
			self.selected_category = 1
		self.categories_frame.winfo_children()[self.selected_category].icon_lbl.configure(image=self.selected_YES)
		self.categories_frame.winfo_children()[self.selected_category].icon_lbl.image = self.selected_YES
		self.build_headlines()
	
	# publish link of selected headline on double tap
	def double_tap(self, *args):
		link_json = {}
		link_json["link"] = self.current_headlines[self.headline_titles[self.selected_headline]]
		publish.publish(args[0], "/iotappdev/news/article/link/", link_json, args[1])
	
	# build Category frames
	def build_categories(self):
		self.title_lbl = Label(self.categories_frame, text="News", font=('Arial', 28), fg="white", bg="black")
		self.title_lbl.pack(side=TOP, anchor=NW)
		for category in self.category_names:
			line = Category(self.categories_frame, category, self.category_names[0])
			line.pack(side=TOP, anchor=W)
		self.category_names.insert(0, 'News')
	
	# build Headline frames
	def build_headlines(self):
		try:
			self.selected_headline = 1
			self.current_headlines = {}
			self.headline_titles = []
			# clear previous headlines
			for line in self.headlines_frame.winfo_children():
				line.destroy()
			
			title = Label(self.headlines_frame, text=self.category_names[self.selected_category], font=('Arial', 24), fg="white", bg="black")
			title.pack(side=TOP, anchor=W)
			self.headline_titles.append(self.category_names[self.selected_category])
			
			# limit length of headline to 80 characters
			for article in self.rss_feeds[self.category_names[self.selected_category]].entries:
				if len(article.title) < 80:
					self.headline_titles.append(article.title)
					self.current_headlines[article.title] = article.link
					line = Headline(self.headlines_frame, article.title, (article.title is self.headline_titles[self.selected_headline]))
					line.pack(side=TOP, anchor=W)
				if len(self.headlines_frame.winfo_children()) > 4:
					break
			
		except Exception as error:
			traceback.print_exc()
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
		
		self.category_lbl = Label(self, text=category_name, font=('Arial', 16), fg='white', bg='black')
		self.category_lbl.pack(side=LEFT, anchor=CENTER)


# small frame for displaying the headlines
class Headline(Frame):
	def __init__(self, parent, headline, is_selected):
		Frame.__init__(self, parent, bg='black')
		
		if is_selected:
			icon = Image.open("assets/newspaper_YES.jpg")
		else:
			icon = Image.open("assets/selected_NO.jpg")
		
		icon = icon.resize((14, 14))
		icon = icon.convert('RGB')
		pic = ImageTk.PhotoImage(icon)
		
		self.icon_lbl = Label(self, bg='black', image=pic)
		self.icon_lbl.image = pic
		self.icon_lbl.pack(side=LEFT, anchor=CENTER)
		
		self.headline_lbl = Label(self, text=headline, font=('Arial', 16), fg='white', bg="black")
		self.headline_lbl.pack(side=LEFT, anchor=N)
