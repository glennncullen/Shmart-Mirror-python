import requests
import json
import tkFont
from Tkinter import *
from PIL import Image
from PIL import ImageTk
from datetime import datetime


class Weather(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)
		
		self.ip = ''
		self.location = {}
		self.forecast = []
		self.selected_day = 0
		
		# request to get ip
		try:
			ip_api_url = 'https://api.ipify.org'
			self.ip = requests.get(ip_api_url).text
		except Exception as error:
			#~ traceback.print_exc()
			print "Error requesting ip: %s" % error
		# request to get location
		try:
			location_api_url = 'http://geoplugin.net/json.gp?ip=%s' % self.ip
			response = requests.get(location_api_url)
			self.location = json.loads(response.text)
		except Exception as error:
			#~ traceback.print_exc()
			print "Error requesting location: %s" % error
		# request to get weather data
		try:
			weather_api_key = "7e6cc30a4f8ea38857191b4bf0264bcf"
			weather_api_url = 'http://api.openweathermap.org/data/2.5/forecast?q=%s,%s&mode=json&appid=%s' % ((self.location["geoplugin_countryName"].replace(" ", "_")), self.location["geoplugin_countryCode"], weather_api_key)
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
			#~ traceback.print_exc()
			print "Error requesting weather: %s" % error
		
		self.forecast_frame = Frame(self, bg='black')
		self.forecast_frame.pack(side=RIGHT)
		
		self.build_forecast()
	
	# create frames for forecast
	def build_forecast(self):
		for frame in self.forecast_frame.winfo_children():
			frame.destroy()
		
		for day in self.forecast:
			frame = Day(self.forecast_frame, day, (day is self.forecast[self.selected_day]))
			frame.pack(side=TOP, anchor=CENTER, pady=20, fill=X)
	
	# move day in direction given
	def change_day(self, direction):
		#~ previous_lbl = self.forecast_frame.winfo_children()[self.selected_day].day_lbl
		#~ remove_underline = tkFont.Font(previous_lbl, previous_lbl.cget("font"))
		#~ remove_underline.configure(underline = False)
		#~ previous_lbl.configure(font=remove_underline)
		#~ print "before: %s" % self.selected_day
		self.selected_day += direction
		#~ print "after: %s" % self.selected_day
		if self.selected_day < 0:
			self.selected_day = 5
		elif self.selected_day > 5:
			self.selected_day = 0
		#~ print "conditions: %s" % self.selected_day, "\n"
		#~ next_lbl = self.forecast_frame.winfo_children()[self.selected_day].day_lbl
		#~ underline = tkFont.Font(next_lbl, next_lbl.cget("font"))
		#~ underline.configure(underline = True)
		#~ next_lbl.configure(font=underline)
	
	def create_entry(self, entry):
		new_entry = {}
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
class Day(Frame):
	def __init__(self, parent, forecast, selected):
		Frame.__init__(self, parent, bg='black')
		
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
		
		if selected:
			underline = tkFont.Font(self.day_lbl, self.day_lbl.cget("font"))
			underline.configure(underline = True)
			self.day_lbl.configure(font=underline)
		
