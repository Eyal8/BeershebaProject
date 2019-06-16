from networkx_visualization import *

# decide which objects to add to the map (all together is overwhelming)

def visualize_fire_hydrants_network(distance=0.1):
  coordinates = defaultdict(tuple)
  df_fire = pd.read_csv("./Fire_Hydrant.csv")
  df_fire['Name'] = df_fire['Id']
  df_fire = df_fire[['X', 'Y', 'Name', 'Id']]
  for row in df_fire.itertuples():
    coordinates[row[4]] = (row[1], row[2], row[3], 'red')
  min_x = df_fire['X'].min()
  max_x = df_fire['X'].max()
  min_y = df_fire['Y'].min()
  max_y = df_fire['Y'].max()
  fire_hydrants_edges = pd.read_csv("./all_hydrants_edges.csv")
  g = create_graph(fire_hydrants_edges, coordinates, distance)
  draw_nx(g, min_x, max_x, min_y, max_y, str(distance))
  return g

def display_isolated_objects(objects, threshold, neighborhoods):
  '''
  display objects that are not within a given threshold to any fire hydrant
  :param objects: the types of object to present
  :param threshold: the distance threshold to a fire hydrant
  :param neighborhoods: the neighborhoods to present the data in
  :return:
  '''

  g = create_all_graphs(objects, threshold)
  relevant_nodes = nodes_per_neighborhood(g, neighborhoods)
  isolated_nodes = get_isloated_nodes(g, relevant_nodes)
  m = folium.Map(location=[31.2530, 34.7915], tiles='Stamen Terrain',
                 zoom_start=13, control_scale=True, prefer_canvas=True)
  colors = nx.get_node_attributes(g, 'color')
  poses = nx.get_node_attributes(g,'x')
  names = nx.get_node_attributes(g, 'name')
  for node in g.nodes:
    if node in isolated_nodes:
      icon = folium.Icon(**{'prefix': 'fa', 'color': colors[node], 'icon': 'arrow-up'})
      folium.Marker([poses[node][1], poses[node][0]], popup=str(names[node]), icon=icon).add_to(m)
  return m

if __name__ == "__main__":
  m = display_isolated_objects(['community-centers'], 0.01, ['Alef', 'Dalet', 'Vav'])



  # # # Create a Map instance
  # m = folium.Map(location=[31.2530, 34.7915], tiles='Stamen Terrain',
  #                zoom_start=13, control_scale=True, prefer_canvas=True)
  # # Alternative layouts: Stamen Toner, OpenStreetMap, Stamen Terrain
  # objects_chosen = [objects[8], objects[9]]
  # neighborhood_chosen = ['Gimel', 'Dalet', 'Alef', 'Vav']
  #
  # #troublesome_objects = find_unconnected_nodes(g)
  # #print(troublesome_objects)
  # display_objects(m, objects_chosen, None, None)
  # # display_each_object_separatly()
  # # Filepath to the output
  outfp = "./Folium_maps/test.html"
  #
  # # Save the map
  m.save(outfp)


  #fire_hydrants_centrality()
