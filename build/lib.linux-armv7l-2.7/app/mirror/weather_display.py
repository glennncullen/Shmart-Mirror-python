import requests
import json
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
			for entry in weather:
				if "12:00:00" in entry["dt_txt"]:
					new_entry = {}
					entry["day"] = datetime.strptime(entry["dt_txt"][:10], '%Y-%m-%d').strftime('%A')
					self.forecast.append(entry)
			for entry in self.forecast:
				print entry, "\n"
				#~ print entry["dt"], entry["main"], entry["weather"], entry["dt_txt"], "\n"
		except Exception as error:
			#~ traceback.print_exc()
			print "Error requesting weather: %s" % error
