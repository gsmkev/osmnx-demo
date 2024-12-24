import geopandas as gpd
import osmnx as ox

# turn it back on and turn on/off logging to your console
ox.settings.use_cache = True
ox.settings.log_console = False

# you can also pass multiple places as a mixed list of strings and/or dicts
places = [
    "Lambare, Paraguay",
    "Asuncion, Paraguay",
]
G = ox.graph.graph_from_place(places, truncate_by_edge=True, network_type="drive")

# save to disk as GeoPackage file then plot
ox.io.save_graph_geopackage(G)
fig, ax = ox.plot.plot_graph(G, node_size=0, edge_color="w", edge_linewidth=0.2)