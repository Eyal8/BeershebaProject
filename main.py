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



def get_edges_to_hydrants(df, dataset_name):
  df = df.replace(np.nan, 'unknown', regex=True)
  fire_df = pd.read_csv("./Fire_Hydrant.csv")
  fire_df['Id'] = fire_df.index + 1
  edges = pd.DataFrame(columns=['source', 'dest', 'dist'])
  for row in fire_df.itertuples():
    for row2 in df.itertuples():
      cur_dist = distance.distance((row[2], row[1]), (row2[2], row2[1]))
      edge = pd.DataFrame([[row[4], row2[3], cur_dist]],
                          columns=['source', 'dest', 'dist'])
      edges = edges.append(edge)
  edges['dist'] = edges['dist'].apply(lambda x: float(str(x).split()[0]))
  edges = edges[edges['dist'] != 0.0]
  edges.to_csv("Edges/" + dataset_name, index=False)


def get_fire_hydrants_edges(start, end):
  df = pd.read_csv("./Datasets/Fire_Hydrant.csv")
  df['Id'] = df.index + 1
  df2 = df.iloc[start:end]
  edges = pd.DataFrame(columns=['source', 'dest', 'dist'])
  #i = 0
  for row in df.itertuples():
    for row2 in df2.itertuples():
      cur_dist = distance.distance((row[2], row[1]), (row2[2], row2[1]))
      edge = pd.DataFrame([[row[4], row2[4], cur_dist]],
                          columns=['source', 'dest', 'dist'])
      edges = edges.append(edge)

    #print("hayush " + str(i))
    #i += 1
  edges['dist'] = edges['dist'].apply(lambda x: float(str(x).split()[0]))
  edges = edges[edges['dist'] != 0.0]
  edges.to_csv("Edges/hydrants_edges" + str(start) + ".csv", index=False)

def unite_csv():
  edges = pd.DataFrame(columns=['source', 'dest', 'dist'])
  for file in os.listdir("./"):
    if "%" in file:
      current = pd.read_csv(file)
      edges = edges.append(current)
  edges.to_csv("all_hydrants_edges.csv", index=False)

def create_graph(df=None, coordinates=None, threshold=0.3):
  '''
  create the graph given df of edges and coordinates
  :param df:
  :param coordinates:
  :param threshold: edges with distance bigger than the threshold will be discarded from the graph
  :return: networkx graph object
  '''
  g = nx.Graph()
  for key, value in coordinates.items():
    g.add_node(key, x=(value[0], value[1]), color=value[2])
  #for i, r in df.iterrows():
  #  g.add_node(r['source'], x=coordinates[r['source']])
  #  g.add_node(r['dest'], x=coordinates[r['dest']])
  df = df[df['dist'] < threshold]
  edges_list = [(r['source'], r['dest']) for i, r in df.iterrows()]
  g.add_edges_from(edges_list)
  return g

def draw_nx(g, min_x, max_x, min_y, max_y, distance):
  plt.figure(figsize=(30, 30))
  color = nx.get_node_attributes(g, 'color')
  pos = nx.get_node_attributes(g,'x')
  nx.draw(g, pos=pos, node_color=color.values(), with_labels=True)
  plt.xlim([min_x, max_x])
  plt.ylim([min_y, max_y])
  plt.axis('on')
  plt.show()
  #plt.savefig('edges_network_' + distance + '.png')

def add_objects_to_map(file_path=None, name='name', map=None, icon_prefix='fa', icon_color='blue', icon_type='arrow-up',
                       neighborhood_coordinates=None):
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
    label = str(df.iloc[i][name])
    icon = folium.Icon(**{'prefix': icon_prefix, 'color': icon_color, 'icon': icon_type})
    if neighborhood_coordinates == None:
      folium.Marker([long_coord, lat_coord], popup=label, icon=icon).add_to(map)
    else: # check if within the neighborhood's coordinates
      in_long = long_coord >= neighborhood_coordinates[0] and long_coord <= neighborhood_coordinates[1]
      in_lat = lat_coord >= neighborhood_coordinates[2] and lat_coord <= neighborhood_coordinates[3]
      if in_lat and in_long:
        folium.Marker([long_coord, lat_coord], popup=label, icon=icon).add_to(map)

def display_objects(objects_chosen, neighborhoods_chosen):
  '''
  add the different objects to the map
  :param objects_chosen: The kind of objects to display (list)
  :param neighborhoods_chosen: The neighborhood to display the objects in (list)
  :return:
  '''
  for object in objects_chosen:
    for neighborhood in neighborhoods_chosen:
      add_objects_to_map(file_path="./Datasets/" + object[0] + ".csv", name=object[1], map=m, icon_prefix='fa',
                         icon_color=object[2],neighborhood_coordinates=neighborhoods_coordinates[neighborhood])

# draw more specifically
def display_each_object_separatly():
  # fire hydrants
  add_objects_to_map(file_path="./Datasets/Fire_Hydrant.csv", name='Id', map=m, icon_prefix='fa', icon_color='red',
                     neighborhood_coordinates=neighborhoods_coordinates['Dalet'])
  # community centers
  add_objects_to_map(file_path="./Datasets/community-centers.csv", name='Name', map=m, icon_prefix='fa', icon_color='blue',
                     neighborhood_coordinates=neighborhoods_coordinates['Dalet'])
  # daycare
  add_objects_to_map(file_path="./Datasets/daycare.csv", map=m,  icon_prefix='fa', icon_color='pink',
                     neighborhood_coordinates=neighborhoods_coordinates['Dalet'])
  # gas stations
  add_objects_to_map(file_path="./Datasets/gas_stations.csv", name='Name', map=m, icon_prefix='fa', icon_color='green',
                     neighborhood_coordinates=neighborhoods_coordinates['Dalet'])
  # educational institutions
  add_objects_to_map(file_path="./Datasets/EducationalInstitutions.csv", name='Name', map=m, icon_prefix='fa', icon_color='purple',
                     neighborhood_coordinates=neighborhoods_coordinates['Dalet'])
  #  health clinics
  add_objects_to_map(file_path="./Datasets/HealthClinics.csv", name='Name', map=m, icon_prefix='fa', icon_color='orange')
  # playgrounds
  add_objects_to_map(file_path="./Datasets/playgrounds.csv", name='Name', map=m, icon_prefix='fa', icon_color='black')
  # sport fields
  add_objects_to_map(file_path="./Datasets/Sport.csv", name='Name', map=m, icon_prefix='fa', icon_color='gray')
  # synagogues
  add_objects_to_map(file_path="./Datasets/Synagogue.csv", name='Name', map=m, icon_prefix='fa', icon_color='cadetblue')



neighborhoods_coordinates = defaultdict(list) # [lat_start, lat_end, long_start, long_end]
neighborhoods_coordinates['Alef'] = [31.244009, 31.251860, 34.782724, 34.797824]
neighborhoods_coordinates['Bet'] = [31.250628, 31.258846, 34.775928, 34.798577]
neighborhoods_coordinates['Gimel'] = [31.244801, 31.256028, 34.797427, 34.814157]
neighborhoods_coordinates['Dalet'] = [31.258413, 31.272858, 34.785338, 34.804906]


# decide which objects to add to the map (all together is overwhelming)
objects = {1:['community-centers', 'blue'],
           2:['daycare', 'purple'],
           3:['gas_stations', 'black'],
           4:['EducationalInstitutions', 'gray'],
           5:['HealthClinics', 'pink'],
           6:['playgrounds', 'green'],
           7:['Sport', 'orange'],
           8:['Synagogue', 'cadetblue']}

if __name__ == "__main__":
  # # Create a Map instance
  m = folium.Map(location=[31.2530, 34.7915], tiles='Stamen Terrain',
                 zoom_start=13, control_scale=True, prefer_canvas=True)
  # # Alternative layouts: Stamen Toner, OpenStreetMap, Stamen Terrain
  # objects_chosen = [objects[0], objects[4]]
  # neighborhood_chosen = ['Gimel', 'Dalet']
  # display_objects(objects_chosen, neighborhood_chosen)
  # # display_each_object_separatly()
  # # Filepath to the output
  # outfp = "beersheba_map.html"
  #
  # # Save the map
  # m.save(outfp)
  #jobs = []
  #for i in range(20):
  #  i = i * 100
  #  p = multiprocessing.Process(target=get_fire_hydrants_edges, args=(i, i + 100))
  #  jobs.append(p)
  #  p.start()
  #jobs = []
  #start = 2000
  #for i in range(6):
  #  if i < 5:
  #	  p = multiprocessing.Process(target=get_fire_hydrants_edges, args=(start, start + 100))
  #  else:
  #	  p = multiprocessing.Process(target=get_fire_hydrants_edges, args=(start, start + 95))
  #  start += 100
  #  jobs.append(p)
  #  p.start()

def unite_edges():
  total_df = pd.DataFrame(columns=['source', 'dest', 'dist'])
  for edge_file in os.listdir('./Edges/'):
    total_df = total_df.append(pd.read_csv('./Edges/' + edge_file), ignore_index=True)
  return total_df

def create_all_graphs():
  total_df = pd.DataFrame(columns=['X', 'Y', 'Name'])

  coordinates = defaultdict(tuple)
  colors = ['blue', 'green', 'yellow', 'pink', 'orange', 'brown', 'purple']
  for i, dataset in enumerate(os.listdir('./Datasets/')):
    color = colors[i]
    df = pd.read_csv('./Datasets/' + dataset)
    df = df[['X', 'Y', 'Name']]
    total_df = total_df.append(df, ignore_index=True)
    for row in df.itertuples():
      coordinates[row[3]] = (row[1], row[2], color)
  df_fire = pd.read_csv("./Fire_Hydrant.csv")
  df_fire['Name'] = df_fire.index + 1
  df_fire = df_fire[['X', 'Y', 'Name']]
  total_df = total_df.append(df_fire, ignore_index=True)
  for row in df_fire.itertuples():
    coordinates[row[3]] = (row[1], row[2], 'red')

  min_x = total_df['X'].min()
  max_x = total_df['X'].max()
  min_y = total_df['Y'].min()
  max_y = total_df['Y'].max()

  distance = 0.2
  g = create_graph(unite_edges(), coordinates, distance)
  draw_nx(g, min_x, max_x, min_y, max_y, str(distance))


create_all_graphs()
# for distance in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]:
#   g = create_graph(df, coordinates, distance)
#   draw_nx(g, min_x, max_x, min_y, max_y, str(distance))

#for dataset in os.listdir('./Datasets/'):
#  if 'commun' not in dataset:
#    df = pd.read_csv('./Datasets/' + dataset)
#    df = df[['X','Y','Name']]
#    get_edges_to_hydrants(df, 'edges_' + dataset)
 
