from collections import defaultdict
import pandas as pd
import numpy as np
import folium
from folium import plugins
from geopy import distance
from geopy.distance import geodesic
import multiprocessing
import os
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

neighborhoods_coordinates = defaultdict(list)  # [lat_start, lat_end, long_start, long_end]
neighborhoods_coordinates['Ramot'] = Polygon(
    [(31.286587, 34.791335), (31.274997, 34.795884), (31.270082, 34.800004), (31.263772, 34.806699),
     (31.267881, 34.817428), (31.272943, 34.828071), (31.280719, 34.825324), (31.280645, 34.821290),
     (31.289374, 34.806184)])
neighborhoods_coordinates['Dalet'] = Polygon(
    [(31.271476, 34.781207), (31.264653, 34.789018), (31.259003, 34.787473), (31.258196, 34.797858),
     (31.255702, 34.798459), (31.256215, 34.810990), (31.257389, 34.812020), (31.274924, 34.796571)])
neighborhoods_coordinates['Vav'] = Polygon(
    [(31.271541, 34.780349), (31.266479, 34.768676), (31.260609, 34.773311), (31.258335, 34.775800),
     (31.258995, 34.787387), (31.263984, 34.789361), (31.270661, 34.781207)])
neighborhoods_coordinates['Bet'] = Polygon(
    [(31.258449, 34.797977), (31.258522, 34.775833), (31.251625, 34.786562), (31.250671, 34.797548),
     (31.257715, 34.797977)])
neighborhoods_coordinates['Gimel'] = Polygon(
    [(31.255238, 34.798757), (31.250762, 34.798070), (31.244891, 34.804765), (31.251642, 34.815751),
     (31.256558, 34.812404)])
neighborhoods_coordinates['Down Town'] = Polygon(
    [(31.250392, 34.797997), (31.245916, 34.796710), (31.243935, 34.793105), (31.239311, 34.797825),
     (31.244522, 34.804434)])
neighborhoods_coordinates['Alef'] = Polygon(
    [(31.243861, 34.793191), (31.248117, 34.797911), (31.250906, 34.797825), (31.252153, 34.786496),
     (31.246356, 34.782719)])
neighborhoods_coordinates['Hei'] = Polygon(
    [(31.246429, 34.782290), (31.252080, 34.770188), (31.258390, 34.775595), (31.252153, 34.786067)])
neighborhoods_coordinates['Tet'] = Polygon(
    [(31.252226, 34.770274), (31.241293, 34.767441), (31.244595, 34.782633), (31.246209, 34.782977),
     (31.251566, 34.771733)])
neighborhoods_coordinates['Yod Alefh'] = Polygon(
    [(31.266313, 34.768557), (31.256849, 34.758429), (31.251933, 34.770102), (31.258610, 34.775595)])
neighborhoods_coordinates['Old Town'] = Polygon(
    [(31.239091, 34.798169), (31.233367, 34.784178), (31.235128, 34.770789), (31.241293, 34.767527),
     (31.244375, 34.782033), (31.246283, 34.782719)])
neighborhoods_coordinates['Ashan'] = Polygon(
    [(31.266844, 34.768721), (31.272053, 34.762885), (31.262222, 34.749495), (31.257012, 34.758593),
     (31.265890, 34.767606)])
neighborhoods_coordinates['Noi_Beka'] = Polygon(
    [(31.239255, 34.798076), (31.230301, 34.802110), (31.225971, 34.797732), (31.218337, 34.774043),
     (31.221861, 34.768550), (31.234044, 34.774472), (31.238447, 34.794986)])
neighborhoods_coordinates['Darom'] = Polygon(
    [(31.230958, 34.803023), (31.225967, 34.797272), (31.220095, 34.799590), (31.220169, 34.804654),
     (31.212021, 34.802336), (31.212681, 34.824738), (31.225380, 34.826026)])
neighborhoods_coordinates['Nahot'] = Polygon(
    [(31.256796, 34.758152), (31.249751, 34.755148), (31.241239, 34.758667), (31.224359, 34.762959),
     (31.226047, 34.771799), (31.234634, 34.776005), (31.237276, 34.768881), (31.242340, 34.767508),
     (31.251953, 34.769997)])

def return_neighborhoods_coordinates():
  return neighborhoods_coordinates
# decide which objects to add to the map (all together is overwhelming)
objects = {1:['community-centers', 'blue'],
           2:['daycare', 'purple'],
           3:['gas_stations', 'cyan'],
           4:['EducationalInstitutions', 'green'],
           5:['HealthClinics', 'pink'],
           6:['Sport', 'orange'],
           7:['Synagogue', 'yellow']}


def add_object_to_map(file_path=None, map=None, icon_prefix='fa', icon_color='blue',
                       icon_type='arrow-up', neighborhood_coordinates=None, specific_objects=None,
                      is_fire_hydrants=False):
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
  if is_fire_hydrants:
    df['Name'] = df['Id']
  df = df.replace(np.nan, 'unknown', regex=True)
  for i in range(len(df)):
    if specific_objects != None:
      if df.iloc[i]['Id'] in specific_objects:
        pass
      else:
        continue
    lat_coord = df.iloc[i]['X']
    long_coord = df.iloc[i]['Y']
    label = str(df.iloc[i]['Name'])
    icon = folium.Icon(**{'prefix': icon_prefix, 'color': icon_color, 'icon': icon_type})
    if neighborhood_coordinates == None:
      folium.Marker([long_coord, lat_coord], popup=label, icon=icon).add_to(map)
    else:  # check if within the neighborhood's coordinates
      p = Point(long_coord, lat_coord)
      if p.within(neighborhood_coordinates):
      #in_long = long_coord >= neighborhood_coordinates[0] and long_coord <= neighborhood_coordinates[1]
      #in_lat = lat_coord >= neighborhood_coordinates[2] and lat_coord <= neighborhood_coordinates[3]
      #if in_lat and in_long:
        folium.Marker([long_coord, lat_coord], popup=label, icon=icon).add_to(map)


def display_objects(map, objects_chosen, neighborhoods_chosen, specific_objects):
  '''
  add the different objects to the map
  :param objects_chosen: The kind of objects to display (list)
  :param neighborhoods_chosen: The neighborhood to display the objects in (list)
  :return:
  '''
  for object in objects_chosen:
    for neighborhood in neighborhoods_chosen:
      add_object_to_map(file_path="./Modified_datasets/" + object[0] + ".csv", map=map, icon_prefix='fa',
                         icon_color=object[1], neighborhood_coordinates=neighborhoods_coordinates[neighborhood],
                        specific_objects=specific_objects, is_fire_hydrants=False)
  # draw fire hydrants
  for neighborhood in neighborhoods_chosen:
    add_object_to_map(file_path="./Fire_Hydrant" + ".csv", map=map, icon_prefix='fa',
                      icon_color='red', neighborhood_coordinates=neighborhoods_coordinates[neighborhood],
                      specific_objects=specific_objects, is_fire_hydrants=True)

# draw more specifically
def display_each_object_separatly(map):
  # fire hydrants
  add_object_to_map(file_path="./Datasets/Fire_Hydrant.csv", map=map, icon_prefix='fa', icon_color='red',
                     neighborhood_coordinates=neighborhoods_coordinates['Dalet'])
  # community centers
  add_object_to_map(file_path="./Datasets/community-centers.csv", map=map, icon_prefix='fa',
                     icon_color='blue',
                     neighborhood_coordinates=neighborhoods_coordinates['Dalet'])
  # daycare
  add_object_to_map(file_path="./Datasets/daycare.csv", map=map, icon_prefix='fa', icon_color='pink',
                     neighborhood_coordinates=neighborhoods_coordinates['Dalet'])
  # gas stations
  add_object_to_map(file_path="./Datasets/gas_stations.csv", map=map, icon_prefix='fa',
                     icon_color='green', neighborhood_coordinates=neighborhoods_coordinates['Dalet'])
  # educational institutions
  add_object_to_map(file_path="./Datasets/EducationalInstitutions.csv", map=map, icon_prefix='fa',
                     icon_color='purple',
                     neighborhood_coordinates=neighborhoods_coordinates['Dalet'])
  # health clinics
  add_object_to_map(file_path="./Datasets/HealthClinics.csv", map=map, icon_prefix='fa',
                     icon_color='orange')
  # sport fields
  add_object_to_map(file_path="./Datasets/Sport.csv", map=map, icon_prefix='fa', icon_color='gray')
  # synagogues
  add_object_to_map(file_path="./Datasets/Synagogue.csv", map=map, icon_prefix='fa',
                     icon_color='cadetblue')


