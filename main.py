# import googlemaps
#
# from datetime import datetime
#
# gmaps = googlemaps.Client(key='Add Your Key here')
#
# # Geocoding an address
# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
#
# # Look up an address with reverse geocoding
# reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))
#
# # Request directions via public transit
# now = datetime.now()
# directions_result = gmaps.directions("Sydney Town Hall",
#                                      "Parramatta, NSW",
#                                      mode="transit",
#                                      departure_time=now)
import pandas as pd
import numpy as np
import folium
from folium import plugins

# Create a Map instance
m = folium.Map(location=[31.2530, 34.7915], tiles='Stamen Terrain',
              zoom_start=13, control_scale=True, prefer_canvas=True)
# Alternative layouts: Stamen Toner, OpenStreetMap, Stamen Terrain

def add_objects_to_map(file_path=None, name='name', map=None, icon_prefix='fa', icon_color='blue', icon_type='arrow-up',
                       lat_start=31.2530, lat_end=31.2530, long_start=34.7915, long_end=34.7915):
  '''
  Adds the objects given as coordinates to the map
  :param file_path: The path to the csv file containing the objects
  :param label: The name of the 'name' field as written in the csv file, if such exists
  :param map: The map to add the objects to
  :param icon_prefix: choose from 'fa' for font-awesome or 'glyphicon' for bootstrap 3
  :param icon_color: choose from the following list: ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
             'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
             'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen',
             'gray', 'black', 'lightgray']
  :param icon_type: choose icon type from ['home', 'glass', 'flag', 'star', 'bookmark']
  :return:
  '''
  if file_path == None or map == None:
    return
  df = pd.read_csv(file_path)
  if name == 'Id':
    df['Id'] = df.index + 1
  df = df.replace(np.nan, 'unknown', regex=True)
  for i in range(len(df)):
    lat_coord = df.iloc[i]['X']
    long_coord = df.iloc[i]['Y']
    label = df.iloc[i][name]

    icon = folium.Icon(**{'prefix': icon_prefix, 'color': icon_color, 'icon': icon_type})
    folium.Marker([long_coord, lat_coord], popup=label, icon=icon).add_to(map)


# add the different objects to the map
# fire hydrants
add_objects_to_map(file_path="./Datasets/Fire_Hydrant.csv", name='Id', map=m, icon_prefix='fa', icon_color='red')
# community centers
add_objects_to_map(file_path="./Datasets/community-centers.csv", name='Name', map=m, icon_prefix='fa', icon_color='blue')
# daycare
add_objects_to_map(file_path="./Datasets/daycare.csv", map=m,  icon_prefix='fa', icon_color='pink')
# gas stations
add_objects_to_map(file_path="./Datasets/gas_stations.csv", name='Name', map=m, icon_prefix='fa', icon_color='green')
# educational institutions
add_objects_to_map(file_path="./Datasets/EducationalInstitutions.csv", name='Name', map=m, icon_prefix='fa', icon_color='purple')
#  health clinics
add_objects_to_map(file_path="./Datasets/HealthClinics.csv", name='Name', map=m, icon_prefix='fa', icon_color='orange')
# playgrounds
add_objects_to_map(file_path="./Datasets/playgrounds.csv", name='Name', map=m, icon_prefix='fa', icon_color='black')
# sport fields
add_objects_to_map(file_path="./Datasets/Sport.csv", name='Name', map=m, icon_prefix='fa', icon_color='gray')
# synagogues
add_objects_to_map(file_path="./Datasets/Synagogue.csv", name='Name', map=m, icon_prefix='fa', icon_color='cadetblue')

# Filepath to the output
outfp = "beersheba_map.html"

# Save the map
m.save(outfp)
