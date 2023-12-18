# Class: CS230--Section 1
# Name: Raine Spearman
# Description: App that allows college students are others to determine crime levels in their area.
# I pledge that I have completed the programming assignment independently.
# I have not copied the code from a student or any source.
# I have not given my code to any student.

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk


df = pd.read_csv("bostoncrime2023_7000_sample.csv",
                 header=0,
                 usecols=["OFFENSE_DESCRIPTION", "DISTRICT", "REPORTING_AREA", "SHOOTING", "DAY_OF_WEEK", "HOUR",
                          "STREET", "MONTH", "Lat", "Long"])

# Intro to the website design
st.markdown("""<h1 style='text-align: center;'>Boston Crime Data Dashboard</h1>""", unsafe_allow_html=True)
st.image("https://www.travelandleisure.com/thmb/_aMbik8KZYsUKc_6_XNeAOzPi84=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/boston-massachusetts-BOSTONTG0221-719aef2eeb1c4929b6c839715e34a69e.jpg", caption="Boston, MA", use_column_width=True)

# Changing district codes to actual city area names
code_to_city = {
    'A1': 'Downtown & Charlestown', 'A15': 'Downtown & Charlestown', 'A7': 'East Boston',
    'B2': 'Roxbury', 'B3': 'Mattapan', 'C6': 'South Boston', 'C11': 'Dorchester',
    'D4': 'South End', 'D14': 'Brighton', 'E5': 'West Roxbury', 'E13': 'Jamaica Plain',
    'E18': 'Hyde Park'
    }
city_names = list(set(code_to_city.values()))

def find_location(location):
    return [code for code, city in code_to_city.items() if city == location]

def time_convert(raw_time, extra=0):
    total_time = raw_time + extra
    if total_time < 0:
        final_user_hour = str(total_time + 12) + " PM"
    elif total_time < 12:
        final_user_hour = str(total_time) + " AM"
    elif total_time == 12:
        final_user_hour = str(total_time) + " PM"
    elif total_time < 24:
        final_user_hour = str(total_time - 12) + " PM"
    else:
        final_user_hour = str(total_time - 24) + " AM"

    return final_user_hour

def crime_info(crime_name):
    crime_info_dict = {
        'M/V - LEAVING SCENE - PROPERTY DAMAGE': {
            'Definition': "leaving the scene of an accident in Massachusetts that causes damage to another vehicle or property is a criminal offense, drivers are responsible to stop after the damage is caused.",
            'Tips': "paying attention to your environment, never drive distracted, follow all traffic signs, and always wait for the police after the damage is caused."
        },
        'ASSAULT - SIMPLE': {
            'Definition': "simple assault is an act intended to arouse fear in a victim, but does not have to involve actual physical contact. Rather, simple assault involves the threat of violence towards another person.",
            'Tips': "avoid walking alone through, be careful of listening to loud music while walking, never pick up hitchhikers, and ensure car doors are locked while driving."
        },
        'M/V ACCIDENT - PROPERTY DAMAGE': {
            'Definition': "property damage often arises from car accidents, damages can also include an individual injured or killed.",
            'Tips': "to avoid property damages in some cases, attempt to stay focused while driving and be a defensive driver on the road at all times."
        },
        'FRAUD - FALSE PRETENSE / SCHEME': {
            'Definition': "obtaining property by false pretenses is a form of larceny which consists of knowingly making false representations of fact.",
            'Tips': "knowing who you are talking to, always check your financial statements, and avoiding sending money to strangers."
        },
        'LARCENY THIEFT FROM MV - NON-ACCESSORY': {
            'Definition': "the law prohibits stealing, receiving, buying, possessing, or concealing a motor vehicle or a trailer that one knew or had reason to know was stolen.",
            'Tips': "lock your car at all times, even when leaving the car for a short time, keep your keys hidden and safely with you."
        },
        'MISSING PERSON - NOT REPORTED - LOCATED': {
            'Definition': "describes persons who cannot be found, yet have not been or cannot be reported as missing persons to law enforcement.",
            'Tips': "the main tip is to stay aware of your surroundings at all times. "
        },
        'LARCENY SHOPLIFTING': {
            'Definition': "shoplifting, shop theft, retail theft, or retail fraud is the theft of goods from a retail establishment during business hours.",
            'Tips': "stores should avoid the shoplifting by installing cameras or security guards to monitor individuals."
        },
        'LARCENY THIEFT OF MV PARTS & ACCESSORIES': {
            'Definition': "the law prohibits stealing, receiving, buying, possessing, or concealing a motor vehicle or a trailer that one knew or had reason to know was stolen.",
            'Tips': "lock your car at all times, even when leaving the car for a short time, keep your keys hidden and safely with you."
        },
        'PROERTY - FOUND': {
            'Definition': "Found Property means any property of value other than real property or fixtures thereon, which is abandoned, lost or left unattended in a public place.",
            'Tips': "lock your doors and windows, even when you're at home. If you notice someone loitering outside your building or residence and it seems suspicious, report them to DPS immediately."
        },
        'PROPERTY - LOST/ MISSING': {
            'Definition': "property Lost or Missing means any property of value other than real property or fixtures thereon, which is abandoned, lost or left unattended in a public place.",
            'Tips': "lock your doors and windows, even when you're at home. If you notice someone loitering outside your building or residence and it seems suspicious, report them to DPS immediately."
        },
        'INVESTIGATE PROPERTY': {
            'Definition': "in a property crime, a victim's property is stolen or destroyed, without the use or threat of force against the victim.",
            'Tips': "lock your doors and windows, even when you're at home. If you notice someone loitering outside your building or residence and it seems suspicious, report them to DPS immediately."
        },
        'SICK ASSIST - DRUG RELATED ILLNESS': {
            'Definition': "crime regarding drug related illness which can include crimes carried out by individuals on drugs.",
            'Tips': "paying attention to your environment and being careful when walking alone in high crime areas."
        },
        'SICK ASSIST': {
            'Definition': "crime regarding drug related illness which can include crimes carried out by individuals on drugs.",
            'Tips': "paying attention to your environment and being careful when walking alone in high crime areas."
        },
        'VERBAL DISPUTE': {
            'Definition': "Verbal Dispute means argument that turns into verbal assault, often threatening an action of violence.",
            'Tips': "paying attention to your environment, attempting to de escalate arguments, and being careful when walking alone in high crime areas."
        },
    }
    if crime_name in crime_info_dict:
        crime_definition = crime_info_dict[crime_name]['Definition']
        crime_tips = crime_info_dict[crime_name]['Tips']
        return crime_definition, crime_tips
    else:
        return "Definition not available", "Tips not available"

# Gathering inputs from the user
user_location_raw = st.selectbox("Location", sorted(city_names))
user_location = find_location(user_location_raw)
user_day = st.selectbox("Select Day of the Week", sorted(df['DAY_OF_WEEK'].unique()))
user_hour = st.slider("Select Hour", min_value=0, max_value=23)
user_raw_data = st.toggle("Show Raw Data Table After Dashboard?")

# Title for the bar graph segment
st.markdown("""<h1 style='text-align: center;'>Crime Hour by Hour Breakdown</h1>""", unsafe_allow_html=True)
st.write("The bar graph below shows a breakdown of the crime for each hour of the day, based on the location and day of the week that the user submitted. This can allow you to avoid times of higher crime in the area.")

# Filter the data by day of week and location, then group hours together for bar graph
count_hourly_crime = df[(df['DAY_OF_WEEK'] == user_day) &
                        (df['DISTRICT'] == user_location[0])].groupby("HOUR").size().reset_index(name = "Crime Count")

# Designing the bar chart below
hour_labels = ["12AM", "1AM", "2AM", "3AM", "4AM", "5AM", "6AM", "7AM", "8AM", "9AM", "10AM", "11AM",
               "12PM", "1PM", "2PM", "3PM", "4PM", "5PM", "6PM", "7PM", "8PM", "9PM", "10PM", "11PM"]
tick_positions = list(range(24))
plt.figure(figsize=(14, 6))
plt.bar(count_hourly_crime["HOUR"], count_hourly_crime["Crime Count"])
plt.xlabel("Hour of the Day", fontsize = 14)
plt.ylabel("Total Crime Count", fontsize = 14)
plt.xticks(ticks = tick_positions, labels = hour_labels)
st.pyplot(plt)                                                          # This publishes the bar graph

# Title for the pie graph segment
st.markdown("""<h1 style='text-align: center;'>Crime Percentage Breakdown</h1>""", unsafe_allow_html=True)
st.write("Pie chart shows the type of crime based on your inputs. This provides guidance on the type of crime to be on the lookout for.")

# Crafting the data for the pie chart, then use data filtered for raw data later on
filter_data = df[
    (df['DAY_OF_WEEK'] == user_day) &
    (df['DISTRICT'] == user_location[0]) &
    ((df['HOUR'] >= user_hour - 1) & (df['HOUR'] <= user_hour + 1))
]
crime_count = filter_data["OFFENSE_DESCRIPTION"].value_counts()

# Creating the pie chart graph
fig, ax = plt.subplots()
ax.pie(crime_count, labels=crime_count.index, autopct='%1.1f%%', startangle=90)
ax.axis('equal')
st.pyplot(fig)

monthly_crime_count = df.groupby(['MONTH']).size().reset_index(name='Total Crimes')

# Line graph of the monthly line graph plot
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
plt.figure(figsize = (10, 6))
plt.plot(monthly_crime_count['MONTH'], monthly_crime_count['Total Crimes'], marker='o')
plt.xlabel('Month')
plt.ylabel('Total Crimes (out of 7000 sample size)')
plt.xticks(range(1, 13), months)
plt.grid(False)

# Display the pyplot on the web page
st.markdown("<h1 style='text-align: center;'>Total Crime of Boston by Month</h1>", unsafe_allow_html=True)
st.write(f"The graph below shows the total crime of Boston per month, which is not adjusted by filters. The major "
         f"takeaway is to showcase the trend in total crime within Boston.")
st.pyplot(plt)

# Formatting for max crime and how to prevent
st.markdown("<h1 style='text-align: center;'>Avoiding High Crime</h1>", unsafe_allow_html=True)
most_common_crime = filter_data['OFFENSE_DESCRIPTION'].value_counts().idxmax()
st.write(f"Based on the pie chart, the most common type of crime is {most_common_crime}.")

crime_definition, crime_tips = crime_info(most_common_crime)

st.write(f"{most_common_crime} is considered {crime_definition}.")
st.write(f"Tips to avoid {most_common_crime} are {crime_tips}")

# Title for the map function
st.markdown("<h1 style='text-align: center;'>Crime Map</h1>", unsafe_allow_html=True)
st.write("Map function shows where most of the crime is taking place, based on your inputs.")

# Crafting the map function
st.pydeck_chart(
    pdk.Deck(
        map_style = "mapbox://styles/mapbox/light-v9",
        initial_view_state = pdk.ViewState(
            latitude = filter_data['Lat'].mean(),
            longitude = filter_data['Long'].mean(),
            zoom = 12,
            pitch = 50,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data = filter_data,
                get_position = "[Long, Lat]",
                get_radius = 50,
                get_fill_color = [255, 0, 0],
                pickable = True,
                auto_highlight = True,
            ),
        ],
    )
)

# Column naming information to design the ending raw data table
use_columns = ["OFFENSE_DESCRIPTION", "SHOOTING", "DAY_OF_WEEK", "HOUR", "STREET"]
name_columns = ["Type of Crime Reported", "Shooting?", "Day of Week", "Hour", "Street"]

filter_data = filter_data[use_columns].rename(columns = dict(zip(use_columns, name_columns)))

# Output the raw data table for the end of the website
if user_raw_data == True:
    st.markdown("<h1 style='text-align: center;'>Raw Data Table</h1>", unsafe_allow_html=True)
    st.write(f"Raw Data of Crime in {user_location_raw} on {user_day} from {time_convert(user_hour, -1)} to {time_convert(user_hour, 1)}")
    st.dataframe(filter_data)