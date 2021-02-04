'''
EYH Room3 Group B - BioBuild Control Panel (BBCP) prototype v0.1
This is a simple program that takes both forecasted and live data from the OpenWeatherMap API.
The program displays the data using matplotlib, then it uses the data to control one servo motor.
This itates the control of the opening of the dome windows to control inside temperature.

Improvements to be made: 
Indoor sensors, more motors, better GUI. 
'''

import requests
from pprint import pprint
import json
import time
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import pyformulas as pf 
import RPi.GPIO as GPIO
import time

servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(2.5) # Initialization

###########################
#API key
API_key = "cf80758e4c8fe865568fa33ee848d480"
#choose the city
city_name = 'Brighton,UK'#input("enter a city name: ")


############################
#url for the 3h forecast
base_url_3hforecast = "https://api.openweathermap.org/data/2.5/forecast?" # change weather for instant data, change to forecast for 3 hour data for 5 days. 
# This is final url. This is concatenation of base_url, API_key and city_id
Final_url1= base_url_3hforecast + "q=" + city_name + "&units=metric" + "&appid=" + API_key # remove "&units=metric" for temperature in kelvin


###############################
#url for the current weather
base_url_current_weather = "https://api.openweathermap.org/data/2.5/weather?" # change weather for instant data, change to forecast for 3 hour data for 5 days. 
# This is final url. This is concatenation of base_url, API_key and city_id
Final_url2 = base_url_current_weather + "q=" + city_name + "&units=metric" + "&appid=" + API_key # remove "&units=metric" for temperature in kelvin


####################################
#manipulating the data for both datasets
# these variables contain the JSON data which the API returns
forecastWeatherData = requests.get(Final_url1).json()# gets the data for the weather forecast.
currentWeatherData = requests.get(Final_url2).json()#gets the data for the current weather at the desired location
#turn it into json data 
jsonForecast = json.dumps(forecastWeatherData)
jsonCurrent = json.dumps(currentWeatherData)
#deserealise the data 
forecast = json.loads(jsonForecast)
weather = json.loads(jsonCurrent) #you can pprint this to see the json data

######################
#this is to get the current time
local_time = time.ctime(time.time())
print(local_time)

#pprint(weather)#change to forecast for the forecast data over 5 days in 3 hour increments
#day is split into 8 sections - 00:00, 03:00, 06:00,09:00, 12:00, 15:00,18:00, 21:00
#the api takes the 'soonest' 3 hour section

style.use("fivethirtyeight")#select the style of graphs that you want to use
p.ChangeDutyCycle(0) #set motor to standard position first
while True:
	timeAndDateArray = []
	temperatureArray = []
	feelsLikeArray = []
	liveTemp = []
	liveTime = []
	liveFeelsLike=[]
	for i in range(17):#fill the arrays with the new data from the api
		timeAndDateArray.append(forecast['list'][i]['main']['temp'])
		temperatureArray.append(time.strftime("%d:%H:%M", time.gmtime(forecast['list'][i]['dt'])))
		feelsLikeArray.append(forecast['list'][i]['main']['feels_like'])
	liveTemp.append((weather['main']['temp'])*1)#take live readings for temperature
	#liveTemp.append(weather['main']['feels_like'])
	liveTime.append(time.strftime("%d:%H:%M", time.gmtime(weather['dt'])))#take live time from json data.
	##########
	fig, (ax1,ax2) = plt.subplots(2,1,figsize=(19,10)) #make a figuse and select its size
	plt.title('Weather Forecast for '+ city_name, fontdict=None, pad=None)
	plt.xlabel("Time (Date,Hour,Minute)")#give the forecast some labels
	plt.ylabel("Temperature (degrees C)")
	
	ax1.plot(temperatureArray,timeAndDateArray,'-.',lw=2.0,label = 'Temperature Outside (degC)')#plot the outside forecasted temperature
	ax1.plot(temperatureArray,feelsLikeArray,'--',lw=2.0, label = 'Feels like temperature (degC)')#plot the outside forecasted feels like temperature
	ax1.legend(loc="upper left") #give it a legend
	
	plt.bar(liveTime,liveTemp,color ='red',width = 0.2)#display the live temperature at the location
	ax2.grid(color='#95a5a6', linestyle='--', linewidth=2, axis='y', alpha=0.7)#give the bar chart a grid
	plt.ylim([-10,50])#set temperature display limits (like a thermometer)
	
	#control structure for the servo motor
	if liveTemp[0]>20:
		p.ChangeDutyCycle(5)
	elif liveTemp[0]<=20:
		p.ChangeDutyCycle(12.5)
	
	plt.show()#show the figure
	time.sleep(1)#when the figure closes stop for 1 second
	fig.clear()#clear the figure before starting again.
