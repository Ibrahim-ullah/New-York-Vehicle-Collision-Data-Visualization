# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 00:51:20 2020

@author: himu
"""


import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

st.title("Motor Vehicle Collision in New York City")
st.markdown("This application is streamlit dashboard to analyze motor vehicle collisions in NYC")\
    
@st.cache(persist = True)
def load_data(nrows):
    data = pd.read_csv("Motor_Vehicle_Collisions_Crashes.csv", nrows = nrows, parse_dates=[['CRASH DATE','CRASH TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace = True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns',inplace = True)
    data.rename(columns={'crash date_crash time':'crash_date_time'}, inplace=True)
    data.rename(columns={'number of persons injured':'number_of_persons_injured'}, inplace = True)
    data.rename(columns={'on street name':'on_street_name'}, inplace=True)
    data.rename(columns={'number of pedestrians injured':'injured_pedestrians'}, inplace=True)
    data.rename(columns={'number of cyclist injured':'injured_cyclists'}, inplace=True)
    data.rename(columns={'number of motorist injured':'injured_motorists'}, inplace=True)
    return data

data = load_data(10000)
original_data = data   

st.header('Where are the most people injured')
injured_people = st.sidebar.slider("Number of people injure in vehicle collision",0,19)
st.map(data.query("number_of_persons_injured >= @injured_people")[["latitude","longitude"]].dropna(how="any"))

st.header("How many collisions occur during a given time period of a day")
hour = st.sidebar.slider("Hour to look at",0,24)
data = data[data['crash_date_time'].dt.hour == hour]


st.markdown("Vehicle collision between {} and {}".format(hour, (hour + 1)))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
        "latitude": midpoint[0],
        "longitude": midpoint[1],
         "zoom": 11,
         "pitch":50,
        },
    
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['crash_date_time','latitude','longitude']],
            get_position = ['longitude','latitude'],
            radius = 100,
            extruded = True,
            pickable =  True,
            elevation_scale = 4,
            elevation_range = [0,1000]
            )
        ]
    ))


st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data['crash_date_time'].dt.hour >= hour) & (data['crash_date_time'].dt.hour < (hour + 1))
    ]
hist = np.histogram(filtered['crash_date_time'].dt.minute, bins = 60, range = (0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes',hover_data=['minute','crashes'],height=400)
st.write(fig)

if st.checkbox("show raw data", False):
    st.subheader("Raw data")
    st.write(data)


st.header("top 5 streets which are prone to accident most")
select = st.sidebar.selectbox("People face accident most",['Pedestrians','Cyclists','Motorists'])
 
if select == 'Pedestrians':
     st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name","injured_pedestrians"]].sort_values(by=['injured_pedestrians'],ascending=False).dropna(how='any')[:5])
     
elif select == 'Cyclists':
     st.write(original_data.query("injured_cyclists >= 1")[["on_street_name","injured_cyclists"]].sort_values(by=['injured_cyclists'],ascending=False).dropna(how='any')[:5])

else:
     st.write(original_data.query("injured_motorists >= 1")[["on_street_name","injured_motorists"]].sort_values(by=['injured_motorists'],ascending=False).dropna(how='any')[:5])


    

    
    
