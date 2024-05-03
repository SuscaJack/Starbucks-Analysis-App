'''
Name:   Jack Susca
CS230:  Section 6
Data:   Starbucks.csv
URL:

Description:
    This program allows users to explore and analyze a database of Starbucks locations around the world using a
streamlit website. The site utilizes a sidebar which allows users to visit one of the 5 pages on the site. The first
page is a home page to welcome the user, which is followed by a map page which displays an interactive map of starbucks
locations in Boston which shows more information about each location when the user hovers their mouse over it. The next
page allows the user to filter through locations based on the timezone and the date when the location was added to the
database, and displays a table of all locations that fit the criteria entered. The next page shows three graphs, one is
a bar chart that shows the top 5 countries with the most Starbucks locations, the second is a pie chart that shows the
ownership distribution of 10,000 starbucks locations around the world, and the third, which is a line chart that shows
when each location in Boston was added to the database. The last page asks the user to input a US city and then displays
the five starbucks locations that are nearest to the center of chosen city.
'''

import pandas as pd
import streamlit as st
import pydeck as pdk
import datetime
#import matplotlib.pyplot as plt
#from geopy.geocoders import Nominatim
#from geopy.distance import geodesic

# read in the data
def read_data():
    return pd.read_csv("starbucks.csv").set_index("Id")

# filter the data
df = read_data()
df_us = df[df['CountryCode'] == 'US'] #[DA4]
df_us_10000 = df_us.head(10000) #first 10,000 in dataset
df_10000 = df.head(10000)
df_table = df[['StarbucksId', 'Name', 'OwnershipType', 'City', 'CountryCode', 'TimezoneId']] #columns that will be included in df_table

# define/redefine dataframes
df_boston = df_us_10000[df_us_10000['City'] == 'Boston'] #checks each row in the DataFrame df_us_10000 to see if the value in the 'City' column is equal to 'Boston' - if so, the selected rows are added to the datafram df_boston
df_us_10000['latitude'] = df_us_10000['Latitude'] #[DA7]
df_us_10000['longitude'] = df_us_10000['Longitude'] # create a new column for lowercase name to fit requirements for map functions
df_boston.rename(columns={'Latitude': 'lat', 'Longitude': 'lon', "Name": "Name"}, inplace=True) #[DA1]


# Convert 'FirstSeen' column to datetime format and then extract just dates - removes time
df['FirstSeen'] = pd.to_datetime(df['FirstSeen']).dt.date

# Define get_lat_lon function
def get_lat_lon(location_name):
    geolocator = Nominatim(user_agent="starbucks_locator") #(Module not taught in class) - sets necessary varialbe for geopy library
    location = geolocator.geocode(location_name) # location name is input by user, find lon and lat of city
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Function to calculate distance between two points
def calculate_distance(lat1, lon1, lat2, lon2):
    coords_1 = (lat1, lon1) # lon and lat of input city
    coords_2 = (lat2, lon2) # lon and lat of starbucks
    return geodesic(coords_1, coords_2).miles # (Module not taught in class) - returns distance between city center and starbucks location

# Function to find nearest Starbucks locations
def find_nearest_starbucks(location_name, num_results=5): #[PY1] - I used chatGPT to assist with this section of my code.
    lat, lon = get_lat_lon(location_name)                        # Refer to my AI report for more information
    if lat is None or lon is None:
        st.write("Location not found. Please try again.")
        return
    st.write("<span style='font-size:20px;'>Coordinates of the center of your city: </span>", unsafe_allow_html=True)
    st.write("Latitude:", lat, "Longitude:", lon)
    st.write('')
    st.write("<span style='font-size:22px;'>Below are the 5 nearest Starbucks locations to the center of your city: </span>", unsafe_allow_html=True)

    #[PY4] #[DA8] #[DA9]
    distances = [(index, calculate_distance(lat, lon, row['latitude'], row['longitude'])) for index, row in df_us_10000.iterrows()]
    # iterates through each 10000 rows, calculates distance between each location and city by lon and lat

    # sorting the distances list based on the second element of each tuple, which represents the distance from the given location.
    nearest_locations = sorted(distances, key=lambda x: x[1])[:num_results] #[DA1]

    print("Nearest Starbucks locations to {}:".format(location_name))
    for index, distance in nearest_locations:
        location_details = df_us_10000.loc[index]
        st.write('')
        st.write('')
        st.write("Distance From Center of City:", distance, "miles")
        st.write("Location Details:", location_details)
def date_query(start_date, end_date): #[PY2] #[PY3]
    st.subheader('Filter by Dates:')
    min_date = datetime.date(2013, 12, 8)
    max_date = datetime.date(2017, 2, 3)
    start_date = st.date_input('Start Date', start_date, min_value = min_date, max_value = max_date) #[ST1]
    end_date = st.date_input('End Date', end_date, min_value = min_date, max_value = max_date)

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    return start_date, end_date
def filter_data(df, start_date, end_date):
        #[DA7]
        df_table = df[['StarbucksId', 'Name', 'FirstSeen', 'City', 'CountryCode', 'TimezoneId']]
        df_table['FirstSeen'] = pd.to_datetime(df_table['FirstSeen'], format='%m/%d/%Y %I:%M:%S %p')

        #[DA5]
        filtered_df = df_table[(df_table['FirstSeen'] >= start_date) & (df_table['FirstSeen'] <= end_date)]
        return filtered_df
def main():
    page_options = ["Home Page", "Map of Starbucks in Boston", "Filtered Locations", "Graphs", "Nearest Starbucks Location"]
    selected_page = st.sidebar.selectbox(options=page_options, label="Select Page") #[ST4]

    if selected_page == "Home Page":
        st.title('Worldwide Starbucks Locations') #[ST4]
        st.write('By: Jack Susca')
        st.write("<span style='font-size:25px;'>Welcome to my program! </span>", unsafe_allow_html=True)
        st.write('Please visit the sidebar to select a page.')

        #[ST4]
        st.image("https://upload.wikimedia.org/wikipedia/commons/d/d6/Starbucks_logo.jpg", caption="Starbucks Logo", use_column_width=True)

    elif selected_page == "Map of Starbucks in Boston": #[VIZ4] - Displays a detailed map with Starbucks locations

        st.title('Starbucks Locations in Boston') #[ST4]

        #[ST4]
        st.write("<span style='font-size:20px;'>Below is a map of all Starbucks locations in Boston</span>", unsafe_allow_html=True)
        st.write('Hover over a location to see more details.')

        view_city = pdk.ViewState(
            latitude=df_boston["lat"].mean(),
            longitude=df_boston["lon"].mean(),
            zoom=11.5,
            pitch=20)
        layer1 = pdk.Layer("ScatterplotLayer",
                           data=df_boston[["Name", "lon", "lat", "PostalCode", "PhoneNumber"]],
                           get_position=["lon", "lat"],
                           get_radius=150,
                           get_color=[45, 105, 23],  #[ST4]
                           pickable=True)
        tool_tip = {"html": "<b>Location Name:</b> {Name} <br> <b>Phone Number:</b> {PhoneNumber} <br> <b>Postal Code:</b> {PostalCode}",
                    "style": {"backgroundColor": "Green",
                              "color": "white"}}   #[ST4]
        map = pdk.Deck(
            initial_view_state=view_city,
            layers=[layer1],
            tooltip=tool_tip
        )
        st.pydeck_chart(map)

    elif selected_page == "Filtered Locations":
            st.title('Starbucks Locations Filter')
            st.subheader('Filter by Time Zone:') #[ST4]
            timezones = df_10000['TimezoneId'].unique()
            selected_timezone = st.selectbox('Select Time Zone', timezones) #[ST2]
            filtered_by_timezone = df_10000[df_10000['TimezoneId'] == selected_timezone]

            start_date, end_date = date_query(datetime.date(2013, 12, 8), datetime.date(2017, 2, 3))
            filtered_data = filter_data(filtered_by_timezone, start_date, end_date)
            filtered_data_sorted = filtered_data.sort_values(by='StarbucksId', ascending=True) #[DA2]

            # Display filtered data
            st.dataframe(filtered_data_sorted) #[ST7]



    elif selected_page == "Graphs":
        #[DA5]
        df_top5 = df_10000[(df_10000["CountryCode"] == "US") | (df_10000["CountryCode"] == "CA") | (df_10000["CountryCode"] == "CN") | (df_10000["CountryCode"] == "JP") | (df_10000["CountryCode"] == "KR")]
        df_top5 = pd.DataFrame({
            'CountryCode': df_top5["CountryCode"],
        })

        def plot_starbucks_locations(df): #[VIZ1]
            # Count the occurrences of each country code
            country_counts = df['CountryCode'].value_counts() #[DA7]

            # Plotting
            fig, ax = plt.subplots(figsize=(10, 6))
            country_counts.plot(kind='bar', color='green')   #[ST4]
            ax.set_xlabel('Top 5 Countries', fontweight="bold")
            ax.set_ylabel('Number of Starbucks', fontweight="bold")
            ax.set_title('Top 5 Countries With Most Starbucks Locations', fontweight="bold")

            # Set x-axis tick labels rotation
            ax.set_xticklabels(country_counts.index, rotation=0)

            st.pyplot(fig) #[ST6]

        st.title('Analyzing Starbucks Locations')
        st.subheader("This bar chart displays the top 5 countries with the most Starbucks locations as well as display the amount of locations in each.")

        # Plot the bar chart
        plot_starbucks_locations(df_top5)

        st.write('')
        st.write('')
        st.write('')


        st.subheader("This pie chart displays the distribution of ownership types of 10000 worldwide Starbucks locations.")

        ownership_counts = df_10000['OwnershipType'].value_counts()

        #[VIZ2]
        # Extracting labels and counts for the pie chart
        labels = ownership_counts.index.tolist()
        counts = ownership_counts.values.tolist()

        # Creating the pie chart
        plt.figure(figsize=(8, 6))
        plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title('Distribution of Starbucks Ownership Types')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(plt.gcf())  # Display the pie chart in Streamlit

        st.write('')
        st.write('')
        st.write('')

        def plot_starbucks_openings_over_time(df): #[VIZ3]
            st.subheader("This line chart shows the date in which each Starbucks location in Boston was added to the database.")

            # Convert 'FirstSeen' column to datetime format
            df['FirstSeen'] = pd.to_datetime(df['FirstSeen'])

            # Group by 'FirstSeen' column and count occurrences
            openings_over_time = df.groupby(pd.Grouper(key='FirstSeen', freq='M')).size()

            # Plotting
            plt.figure(figsize=(10, 6))
            openings_over_time.plot(kind='line', marker='o', color='green')   #[ST4]
            plt.title('Dates when Boston Starbucks Locations were added to the database', fontweight='bold')
            plt.xlabel('Date', fontweight='bold')
            plt.ylabel('Number of Additions', fontweight='bold')
            plt.grid(True)
            plt.xticks(rotation=0)
            st.pyplot(plt)

        plot_starbucks_openings_over_time(df_boston)

    elif selected_page == "Nearest Starbucks Location":
        st.title("Find Nearest Starbucks Locations")
        city_name = st.text_input("Enter a US city name:") #[ST3]
        if st.button("Find Nearest Starbucks"): #[ST5]
            find_nearest_starbucks(city_name)


main()

