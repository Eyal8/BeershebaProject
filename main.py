from networkx_visualization import *

# decide which objects to add to the map (all together is overwhelming)
objects = {1:['community-centers', 'blue'],
           2:['daycare', 'purple'],
           3:['gas_stations', 'cyan'],
           4:['EducationalInstitutions', 'green'],
           5:['HealthClinics', 'pink'],
           6:['Sport', 'orange'],
           7:['Synagogue', 'yellow']}

if __name__ == "__main__":
  # # Create a Map instance
  m = folium.Map(location=[31.2530, 34.7915], tiles='Stamen Terrain',
                 zoom_start=13, control_scale=True, prefer_canvas=True)
  # Alternative layouts: Stamen Toner, OpenStreetMap, Stamen Terrain
  objects_chosen = [objects[1], objects[2]]
  neighborhood_chosen = ['Gimel', 'Dalet', 'Alef', 'Vav']


  #troublesome_objects = find_unconnected_nodes(g)
  #print(troublesome_objects)
  display_objects(m, objects_chosen, neighborhood_chosen, None)
  # display_each_object_separatly()
  # Filepath to the output
  outfp = "./Folium_maps/beersheba_map2.html"

  # Save the map
  m.save(outfp)

  objects_to_display = [objects[1], objects[2], objects[3], objects[5]]
  g = create_all_graphs(objects_to_display)
  print(nodes_per_neighborhood(g, ['Alef']))
  #fire_hydrants_centrality()
