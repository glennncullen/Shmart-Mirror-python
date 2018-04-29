from app.mqtt import publish
import traceback
import requests
import json
import tkFont
from Tkinter import *
from PIL import Image
from PIL import ImageTk
from datetime import datetime


class WeatherFeed(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		self.parent = parent
		
		self.configure(background='black')
		
		# variables for ip
		self.ip = ''
		# dictionary of location 
		self.location = {}
		# array of current forecast jsons
		self.forecast = []
		# currently selected day
		self.selected_day = 0
		
		# image for selected day
		self.selected_YES_img = Image.open("assets/selected_YES.jpg")
		self.selected_YES_img = self.selected_YES_img.resize((16, 16))
		self.selected_YES_img = self.selected_YES_img.convert('RGB')
		self.selected_YES = ImageTk.PhotoImage(self.selected_YES_img)
		
		# image for not selected day
		self.selected_NO_img = Image.open("assets/selected_NO.jpg")
		self.selected_NO_img = self.selected_NO_img.resize((16, 16))
		self.selected_NO_img = self.selected_NO_img.convert('RGB')
		self.selected_NO = ImageTk.PhotoImage(self.selected_NO_img)
		
		# request to get ip through api.ipify.org
		try:
			ip_api_url = 'https://api.ipify.org'
			self.ip = requests.get(ip_api_url).text
		except Exception as error:
			print "Error requesting ip: %s" % error
		# request to get location
		try:
			# using ip, get location from geoplugin and store in location dict
			location_api_url = 'http://geoplugin.net/json.gp?ip=%s' % self.ip
			response = requests.get(location_api_url)
			self.location = json.loads(response.text)
		except Exception as error:
			print "Error requesting location: %s" % error
		try:
			# using subscribed to api key, build request url using it and the location
			weather_api_key = "7e6cc30a4f8ea38857191b4bf0264bcf"
			weather_api_url = 'http://api.openweathermap.org/data/2.5/forecast?q=%s,%s&mode=json&appid=%s' % ((self.location["geoplugin_countryName"].replace(" ", "_")), self.location["geoplugin_countryCode"], weather_api_key)
			# GET weather for location
			response = requests.get(weather_api_url)
			response_json = json.loads(response.text)
			weather = response_json["list"]
			# get current weather
			new_entry = self.create_entry(weather[0])
			new_entry["day"] = "Now"
			self.forecast.append(new_entry)
			# build forecast dict using relevant information
			for entry in weather:
				if "12:00:00" in entry["dt_txt"] and self.forecast[0]["dt_txt"] != entry["dt_txt"]:
					new_entry = self.create_entry(entry)
					self.forecast.append(new_entry)
		except Exception as error:
			traceback.print_exc()
			print "Error requesting weather: %s" % error
		
		self.forecast_frame = Frame(self, bg='black')
		self.forecast_frame.pack(side=RIGHT)
		
		self.build_forecast()
	
	# destroy previous frames and create frames for forecast
	def build_forecast(self):
		for frame in self.forecast_frame.winfo_children():
			frame.destroy()
		for day in self.forecast:
			frame = Day(self.forecast_frame, day, (day is self.forecast[self.selected_day]))
			frame.pack(side=TOP, anchor=CENTER, pady=20, fill=X)
	
	# when display is in focus, publish the forecast for selected day
	def on_focus(self, *args):
		publish.publish(args[0], "/iotappdev/weather/day/", self.forecast[self.selected_day], args[1])
	
	# when flick hat receives vertical gesture, move day in direction given
	def change_vertical_focus(self, direction, *args):
		self.forecast_frame.winfo_children()[self.selected_day].selected_lbl.configure(image=self.selected_NO)
		self.forecast_frame.winfo_children()[self.selected_day].selected_lbl.image = self.selected_NO
		self.selected_day += direction
		if self.selected_day < 0:
			self.selected_day = 5
		elif self.selected_day > 5:
			self.selected_day = 0
		self.forecast_frame.winfo_children()[self.selected_day].selected_lbl.configure(image=self.selected_YES)
		self.forecast_frame.winfo_children()[self.selected_day].selected_lbl.image = self.selected_YES
		publish.publish(args[0], "/iotappdev/weather/day/", self.forecast[self.selected_day], args[1])
	
	# do nothing on double tap
	def double_tap(self, *args):
		return
	
	# when flick hat receives airwheel gesture, move day in direction given
	def airwheel(self, direction, *args):
		self.change_vertical_focus(direction, args[0], args[1])
	
	# on update, reset selected day and rebuild forecast frames
	def update(self):
		self.selected_day = 0
		self.build_forecast()
		return
	
	# create forecast entry taking only relevant data
	def create_entry(self, entry):
		new_entry = {}
		new_entry["location"] = self.location["geoplugin_countryName"]
		new_entry["description"] = entry["weather"][0]["description"]
		new_entry["icon"] = entry["weather"][0]["icon"]
		# convert kelvin to celcius
		new_entry["temperature"] = int(round(entry["main"]["temp"] - 273.15, 0))
		new_entry["temperature_max"] = int(round(entry["main"]["temp_max"] - 273.15, 0))
		new_entry["temperature_min"] = int(round(entry["main"]["temp_min"] - 273.15, 0))
		new_entry["wind_speed"] = entry["wind"]["speed"]
		# convert meteorological degrees to direction
		new_entry["wind_direction"] = self.get_wind_direction(entry["wind"]["deg"])
		new_entry["humidity"] = entry["main"]["humidity"]
		new_entry["day"] = datetime.strptime(entry["dt_txt"][:10], '%Y-%m-%d').strftime('%a')
		new_entry["dt_txt"] = entry["dt_txt"]
		return new_entry
	
	# function to convert meteorological degrees to direction
	def get_wind_direction(self, degrees):
		if degrees <= 11.25:
			return 'N'
		elif degrees >= 11.26 and degrees <= 33.75:
			return 'NNE'
		elif degrees >= 33.76 and degrees <= 56.25:
			return 'NE'
		elif degrees >= 56.26 and degrees <= 78.75:
			return 'ENE'
		elif degrees >= 78.76 and degrees <= 101.25:
			return 'E'
		elif degrees >= 101.26 and degrees <= 123.75:
			return 'ESE'
		elif degrees >= 123.76 and degrees <= 146.25:
			return 'SE'
		elif degrees >= 146.26 and degrees <= 168.75:
			return 'SSE'
		elif degrees >= 168.76 and degrees <= 191.25:
			return 'S'
		elif degrees >= 191.26 and degrees <= 213.75:
			return 'SSW'
		elif degrees >= 213.76 and degrees <= 236.25:
			return 'SW'
		elif degrees >= 236.26 and degrees <= 258.75:
			return 'WSW'
		elif degrees >= 258.76 and degrees <= 281.25:
			return 'W'
		elif degrees >= 281.26 and degrees <= 303.75:
			return 'WNW'
		elif degrees >= 303.76 and degrees <= 326.25:
			return 'NW'
		elif degrees >=326.26:
			return 'N'

# small frame for displaying day's weather
# if day is selected, selected_YES image is 
# put beside day's forecast
class Day(Frame):
	def __init__(self, parent, forecast, selected):
		Frame.__init__(self, parent, bg='black')
				
		if selected:
			self.selected_img = Image.open("assets/selected_YES.jpg")
		else:
			self.selected_img = Image.open("assets/selected_NO.jpg")
		self.selected_img = self.selected_img.resize((16, 16))
		self.selected_img = self.selected_img.convert('RGB')
		self.selected = ImageTk.PhotoImage(self.selected_img)
		self.selected_lbl = Label(self, bg='black', image=self.selected)
		self.selected_lbl.image = self.selected
		self.selected_lbl.pack(side=LEFT, anchor=W)
		
		icon = Image.open("assets/%s.png" % forecast["icon"])
		icon.convert('RGB')
		pic = ImageTk.PhotoImage(icon)
		self.icon_lbl = Label(self, bg='black', image=pic, underline=0)
		self.icon_lbl.image = pic
		self.icon_lbl.pack(side=LEFT, anchor=N, padx=5)
		
		self.temp_lbl = Label(self, text=str(forecast["temperature"]) + u'\N{DEGREE SIGN}', font=('Arial', 18), fg='white', bg='black')
		self.temp_lbl.pack(anchor=W)
		
		self.description_lbl = Label(self, text=forecast["description"], font=('Arial',12), fg='white', bg='black')
		self.description_lbl.pack(anchor=W)
		
		self.day_lbl = Label(self, text=forecast["day"], font=('Arial', 18), fg='white', bg='black')
		self.day_lbl.pack(anchor=W)
		
