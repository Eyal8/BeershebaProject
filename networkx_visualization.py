from collections import defaultdict
import pandas as pd
import numpy as np
from geopy import distance
from geopy.distance import geodesic
import multiprocessing
import os
import networkx as nx
import matplotlib.pyplot as plt
from operator import itemgetter
from folium_visualization import *

def get_edges_to_hydrants(df, dataset_name):
  df = df.replace(np.nan, 'unknown', regex=True)
  fire_df = pd.read_csv("./Fire_Hydrant.csv")
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
  df = pd.read_csv("./Fire_Hydrant.csv")
  df2 = df.iloc[start:end]
  edges = pd.DataFrame(columns=['source', 'dest', 'dist'])
  for row in df.itertuples():
    for row2 in df2.itertuples():
      cur_dist = distance.distance((row[2], row[1]), (row2[2], row2[1]))
      edge = pd.DataFrame([[row[4], row2[4], cur_dist]],
                          columns=['source', 'dest', 'dist'])
      edges = edges.append(edge)

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

def create_graph(df=None, coordinates=None, threshold=0.1):
  '''
  create the graph given df of edges and coordinates
  :param df:
  :param coordinates:
  :param threshold: edges with distance bigger than the threshold will be discarded from the graph
  :return: networkx graph object
  '''
  g = nx.Graph()
  for key, value in coordinates.items():
    if isinstance(value[2], str):
      g.add_node(key, x=(value[0], value[1]), name=value[2], color=value[3])
    else:
      g.add_node(key, x=(value[0], value[1]), name=value[2], color=value[3])

  df = df[df['dist'] < threshold]
  edges_list = [(r['source'], r['dest']) for i, r in df.iterrows()]
  g.add_edges_from(edges_list)
  return g

def draw_nx(g, min_x, max_x, min_y, max_y, distance):
  # plt.figure(figsize=(30, 30))
  # color = nx.get_node_attributes(g, 'color')
  # pos = nx.get_node_attributes(g,'x')
  # names = nx.get_node_attributes(g, 'name')
  # nx.draw_networkx_nodes(g, pos=pos, alpha=0.7, node_color=color.values())
  # nx.draw_networkx_labels(g, pos=pos, labels=names)
  # nx.draw_networkx_edges(g, pos=pos, width=4)
  # plt.xlim([min_x, max_x])
  # plt.ylim([min_y, max_y])
  # plt.axis('on')
  # plt.show()
  # #plt.savefig('edges_network_' + distance + '.png')
  pass
def unite_edges(objects_to_display):
  total_df = pd.DataFrame(columns=['source', 'dest', 'dist'])
  for object in objects_to_display.keys():
    total_df = total_df.append(pd.read_csv('./New_edges/' + 'edges_' + object + '.csv'), ignore_index=True)
  return total_df



def create_all_graphs(objects_to_display, distance=0.03):
  relevant_objects = {k: v for k, v in all_objects.items() if k in objects_to_display}
  total_df = pd.DataFrame(columns=['X', 'Y', 'Name'])
  coordinates = defaultdict(tuple)
  for object, color in relevant_objects.items():
  #colors = ['blue', 'green', 'yellow', 'pink', 'orange', 'brown', 'purple']
  #for i, dataset in enumerate(os.listdir('./Datasets/')):
    df = pd.read_csv('./Modified_datasets/' + object + '.csv')
    df = df[['X', 'Y', 'Name', 'Id']]
    total_df = total_df.append(df, ignore_index=True)
    for row in df.itertuples():
      coordinates[row[4]] = (row[1], row[2], row[3], color)
  df_fire = pd.read_csv("./Fire_Hydrant.csv")
  df_fire['Name'] = df_fire['Id']
  df_fire = df_fire[['X', 'Y', 'Name', 'Id']]
  total_df = total_df.append(df_fire, ignore_index=True)
  for row in df_fire.itertuples():
    coordinates[row[4]] = (row[1], row[2], row[3], 'red')

  min_x = total_df['X'].min()
  max_x = total_df['X'].max()
  min_y = total_df['Y'].min()
  max_y = total_df['Y'].max()

  g = create_graph(unite_edges(relevant_objects), coordinates, distance)
  draw_nx(g, min_x, max_x, min_y, max_y, str(distance))
  return g



def find_unconnected_nodes(g):
  degree_dict = nx.degree_centrality(g)
  degree_zero_nodes = [k for k, v in degree_dict.items() if v == 0 and k > 2595]
  return degree_zero_nodes

def fire_hydrants_centrality():
  df_fire2 = pd.read_csv("C:\\Users\eyal8_000\Desktop\\all_hydrants_edges.csv")
  coordinates = defaultdict(tuple)
  df_fire = pd.read_csv("./Fire_Hydrant.csv")
  df_fire['Name'] = df_fire['Id']
  df_fire = df_fire[['X', 'Y', 'Name', 'Id']]
  for row in df_fire.itertuples():
    coordinates[row[4]] = (row[1], row[2], row[3], 'red')

  g = create_graph(df_fire2, coordinates, 0.2)
  btw_cent = nx.betweenness_centrality(g)
  sorted_btw_cent = [(k, btw_cent[k]) for k in sorted(btw_cent, key=itemgetter(1), reverse=True)]
  print(sorted_btw_cent)
  #draw_nx(g, 0,0,0,0,0)
  # def nx_algorithms(g):
  # only fire hydrants - centrality measurements
  # object nodes - node degrees (check which has 0)
  # subgraphs per neighborhood

def nodes_per_neighborhood(g, neighborhoods):
  nodes = []
  neighborhoods_coordinates = return_neighborhoods_coordinates()
  for node in g.nodes(data='x'):
    p = Point(node[1][::-1])
    for neighborhood in neighborhoods:
      if p.within(neighborhoods_coordinates[neighborhood]):
        nodes.append(node[0])
        break
  return nodes

# decide which objects to add to the map (all together is overwhelming)
all_objects = {'community-centers':'blue',
           'daycare': 'purple',
           'gas_stations': 'cyan',
           'EducationalInstitutions': 'green',
           'HealthClinics': 'pink',
           'Sport': 'orange',
           'Synagogue': 'white',
           'Shelters': 'brown',
           'Sirens': 'black'}

# objects = {1:['community-centers', 'blue'],
#            2:['daycare', 'purple'],
#            3:['gas_stations', 'cyan'],
#            4:['EducationalInstitutions', 'green'],
#            5:['HealthClinics', 'pink'],
#            6:['Sport', 'orange'],
#            7:['Synagogue', 'yellow']}

def get_isloated_nodes(g, relevant_nodes):
  isolated_nodes = []
  for node in g.nodes:
    if node >2595:
      if g.degree[node] == 0 and node in relevant_nodes:
        isolated_nodes.append(node)
  return isolated_nodes

def all_top_central_fire_hydrants():
  g = create_all_graphs(list(all_objects.keys()), 0.03)
  bet_cen = nx.betweenness_centrality(g)
  bet_cen = {k: v for k, v in bet_cen.items() if k < 2596}
  top_hydrants = sorted(bet_cen, key=bet_cen.get, reverse=True)
  poses = nx.get_node_attributes(g, 'x')
  return top_hydrants, poses, bet_cen
