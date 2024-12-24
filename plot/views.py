from django.shortcuts import render
from django.views import View
import multiprocessing as mp
import numpy as np
import osmnx as ox
import humanize
import os
import folium
from django.conf import settings

class RouteView(View):
    def formatTime(self, seconds):
        return humanize.precisedelta(seconds, format="%0.0f")

    def formatDistance(self, meters):
        return humanize.intcomma(meters) + " meters"

    def get(self, request):
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

        # create a folium map centered around the origin
        m = folium.Map(location=origin, zoom_start=13)

        # add the routes to the map
        route1_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route1]
        route2_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route2]

        folium.PolyLine(route1_coords, color='blue', weight=5, opacity=0.7).add_to(m)
        folium.PolyLine(route2_coords, color='red', weight=5, opacity=0.7).add_to(m)

        # ensure the media directory exists
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)

        # save the map to an HTML file
        map_path = os.path.join(settings.MEDIA_ROOT, 'route_map.html')
        m.save(map_path)

        # render the template with the data
        context = {
            'route1_length': self.formatDistance(route1_length),
            'route2_length': self.formatDistance(route2_length),
            'route1_time': self.formatTime(route1_time),
            'route2_time': self.formatTime(route2_time),
            'map_url': os.path.join(settings.MEDIA_URL, 'route_map.html')
        }

        return render(request, 'route.html', context)
