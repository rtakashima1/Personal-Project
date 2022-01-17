# HeatStrokeAlert
# Description:
                # - requires connection of DHT11 to Arduino & Arduino to USB
                # - uses Arduino DHT11 sensor to accumulate [1] Temperature & [2] Relative Humidity (rh) data
                # - retrieves data 5 times and returns the average T,rh
                # - Plots the calculated WBGT index using the average T,rh onto a color coded risk chart

import streamlit as st
import pandas as pd
import base64 
import matplotlib.pyplot as plt
import numpy as np

import serial
import schedule
import time

from requests_html import HTMLSession


# Functions that Calculates [1] Wet Bulb Temperature (wb) & [2] Wet Bulb Global Temperature (wbgt)
def wb(T,rh):
    return T * np.arctan(0.151977 * (rh + 8.313659)**(1/2)) + np.arctan(T + rh) - np.arctan(rh - 1.676331) + 0.00391838 *(rh)**(3/2) * np.arctan(0.023101 * rh) - 4.686035

def fToC(T):
    return (9/5)*T + 32

def wbgt (T,rh):
    return round((0.7*wb(T,rh) + 0.3*T),2)

def average(list):
    return sum(list) / len(list)


# Starts arduino and will collect Temperature and Relative Humidity data from DHT11 sensor
# Returns a list of [T, rh, wbgt]
def runArduino():
    arduino = serial.Serial('COM3',9600)

    try:
        if not arduino.isOpen():
            arduino.open()
    except:
        pass

    list_in_floats = []
    arduino.flushInput()
    arduino.flushOutput()
    arduino.flush()
    arduino_data = arduino.readline()

    decoded_values = str(arduino_data[0:len(arduino_data)].decode("utf-8"))
    list_values = decoded_values.split('x')

    for item in list_values:
        list_in_floats.append((item))

    rh= float((list_in_floats[0]))
    t = float((list_in_floats[1]))
    wbgt_t = round(wbgt(t,rh),1)

    return [t,rh,wbgt_t]



# Web Page Setup - Title & Description
st.title('Heat Stroke Risk Indicator')
st.markdown('##### This app uses local temperature and humidity values taken by Arduino to notifiy whether you are at risk of a heat stroke')
st.text("")

st.markdown('##### Background')
st.write("According to the CDC, an average of 6200 people are hospitalized every year due to heatstrokes and heat-related illnesses. People at greatest risk for heat-related illness include people of ages 65+. This is because as humans age, their abilities to sense heat and to adjust to sudden temperature changes are significantly reduced.")
st.write("The purpose of this app is to calculate Wet Bulb Globe Temperature, which indicates the risk of heatstroke to alert people with decreased capacity to sense and regulate heat. ")
st.text("")

st.markdown('##### What this App does')
st.write("Calculates WBGT in the room the Arduino is placed and plots the measure onto a figure with color coded ranges of risks. It is imperative to keep room conditions within the green range (minimal risk of heatstroke). If WBGT is in any other color zones, immediately cool down and rest.")
st.text("")

st.markdown('##### Key Metrics')
st.write('Wet Bulb Globe Temperature (WBGT) \n- a temperature metric that combines effects of ambient temperature and relative humidity \n- increases as temperature and or relative humidity increases \n- As WBGT increases, so does the risk of heatstroke\n- maintain indoor WBGT levels in the green range below (WBGT < 25) to reduce risk of heatstroke')
st.write('')
st.text("")
st.write('Underneath each metric is the difference between indoor metric minus outdoor metric\n- Note:  Outdoor metrics are calculated based on the input city')



# Web Page Setup - Sidebar: location and start/clear sensor
st.sidebar.title('Step 1. Enter City')
city = st.sidebar.text_input('To compare difference between outdoors')

st.sidebar.title('Step 2. Launch Arduino')
info_bar = st.empty()
start = st.sidebar.button('Start Sensor')
stop = st.sidebar.button('Clear Values')


# Webscrape to retrieve T, rh from google based on 'city' input from user
s = HTMLSession()

url = f'https://www.google.com/search?q=weather+{city.lower()}'

r = s.get(url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'})

temp_global = float(r.html.find('span#wob_ttm', first = True).text)
rh_global = float((r.html.find('span#wob_hm', first = True).text).replace('%',''))
wbgt_global = wbgt(float(temp_global), float(rh_global) )


# Plot data using matplotlib
df = st.empty()
plot = st.empty()
c = 'lightsteelblue'

if start == True:
    base = time.time()
    y = runArduino()
    t,rh,wbgt_t = y
    count = 0
    fig,ax = plt.subplots()
    ax.axhspan(31, 35,0,25,color='black',alpha=0.2, label = 'SEVERE')
    ax.axhspan(28, 31,0,25,color='red',alpha=0.2, label = 'HIGH')
    ax.axhspan(25, 28,0,25,color='yellow',alpha=0.2,label = 'MODERATE')
    ax.axhspan(0, 25,0,25,color='green',alpha=0.2,label = 'MINIMAL')
    list_wbgt = []
    list_temp = []
    list_rh = []

    while count < 5:
        # plt.plot(time.time() - base, wbgt_t, color = 'dimgrey', marker = 'o', markersize = 3)
        count += 1
        y = runArduino()
        t,rh,wbgt_t = y
        list_wbgt.append(wbgt_t)
        list_temp.append(t)
        list_rh.append(rh)
    
    plt.plot(25/2, round(average(list_wbgt)) , color = 'black', marker = 'o', markersize = 5, label = 'Average WBGT')

    plt.xticks(rotation = 90)
    plt.title('Average WBGT', fontweight = 'bold')
    plt.xlabel('Elapsed Time [s]', fontweight = 'bold')
    plt.ylabel('WBGT', fontweight = 'bold')
    plt.xlim(0.00, 25)
    plt.ylim(15, 35)
    plt.legend(loc = 'lower right')

    wbgt_local= round(average(list_wbgt))
    temp_local = round(average(list_temp))
    rh_local = round(average(list_rh))

    st.markdown('---')
    col1, col2, col3 = st.columns(3)
    col1.metric(label="WBGT", value = str(wbgt_local )  + ' C', delta=  str(wbgt_local - wbgt_global) + ' C' ,delta_color = "inverse" )
    col2.metric(label="Temperature", value = str(temp_local) + ' C', delta= str(temp_local - temp_global) + ' C', delta_color = "inverse"   )
    col3.metric(label="Relative Humidity", value = str(rh_local) + '%' , delta= str(rh_local-rh_global) + ' %', delta_color = "inverse")

    st.markdown('---')
    st.pyplot(fig)

    
