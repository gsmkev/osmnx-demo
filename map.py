import multiprocessing as mp

import numpy as np
import osmnx as ox
import humanize
from tabulate import tabulate

def formatTime(seconds):
    return humanize.precisedelta(seconds, format="%0.0f")

def formatDistance(meters):
    return humanize.intcomma(meters) + " meters"

# set up the pool
np.random.seed(0)

# cache the data to disk so it doesn't have to be downloaded again
ox.settings.use_cache = True

# get the street network for a place
G = ox.graph.graph_from_place(
    "Lambare, Paraguay", 
    network_type="drive",
    truncate_by_edge=True,
)

# impute speed on all edges missing data
G = ox.routing.add_edge_speeds(G)

# calculate travel time (seconds) for all edges
G = ox.routing.add_edge_travel_times(G)

# set the origin and destination points
origin = (-25.369323, -57.633488) # Resort Yacht and Paraguayan Golf Club
destination = (-25.284406, -57.563151) # Paseo La Galeria

# find the nodes nearest to the origin and destination points
origin_node = ox.distance.nearest_nodes(G, origin[1], origin[0])
destination_node = ox.distance.nearest_nodes(G, destination[1], destination[0])

# find the shortest path between origin and destination
route1 = ox.routing.shortest_path(G, origin_node, destination_node, weight="length")
route2 = ox.routing.shortest_path(G, origin_node, destination_node, weight="travel_time")

# compare the two routes
route1_length = int(sum(ox.routing.route_to_gdf(G, route1, weight="length")["length"]))
route2_length = int(sum(ox.routing.route_to_gdf(G, route2, weight="travel_time")["length"]))
route1_time = int(sum(ox.routing.route_to_gdf(G, route1, weight="length")["travel_time"]))
route2_time = int(sum(ox.routing.route_to_gdf(G, route2, weight="travel_time")["travel_time"]))

# print the results
data = [
    ["Route 1 (length)", formatDistance(route1_length), formatTime(route1_time)],
    ["Route 2 (travel time)", formatDistance(route2_length), formatTime(route2_time)],
    ["Difference", formatDistance(route2_length - route1_length), formatTime(route2_time - route1_time)]
]

headers = ["Route", "Distance", "Travel Time"]
print(tabulate(data, headers=headers, tablefmt="grid"))

# plot the route
fig, ax = ox.plot.plot_graph_routes(
    G, 
    routes=[route1, route2], 
    route_colors=["c", "m"], 
    route_linewidth=6, 
    node_size=10,
)
