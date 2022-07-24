#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 17 16:48:40 2022

@author: gregor
"""

import geotiler
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import pickle as plk
import numpy as np
import gpxpy
import gpxpy.gpx
import pandas as pd


from geopy.distance import geodesic
from geopy.distance import great_circle

from pyproj import Geod
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
center = (8.915756, 48.448863)



###
# test nearest_points
#point = Point([(0, 0)])
#line = LineString([(1, -2), (1, 2)])
#print(nearest_points(point, line)[1].x, nearest_points(point, line)[1].y)
###


#####

# make tile map
map = geotiler.Map(center=(center[0], center[1]), zoom=16, size=(512, 512))
image = geotiler.render_map(map) 

# box size to get roads in
boxsize = 0.001




#####
# Get distance between Linestring and Coords in meters
def get_dist(ls, point):
    np = nearest_points(ls, point)
    dist = geodesic((np[0].x, np[0].y), (np[1].x, np[1].y)).m
    return dist, (np[0].x, np[0].y), (np[1].x, np[1].y)
    
    
    
    
#####
# get all ways
# load query result form pickle
with open("query_result.plk", "rb") as input_file:
   data = plk.load(input_file)

# get linestring coordinates
linestrings = list()
for way in data.features:
    #print(way)
    if way["geometry"]["coordinates"]:
        linestrings.append(LineString(way["geometry"]["coordinates"]))

#####
# get gpx points
gpx_file = open('Test2.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

points = list()

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            points.append(Point(point.longitude, point.latitude))
            
            
print("Amount GPX points: {}".format(len(points)))
print("Amount Linestrings: {}".format(len(linestrings)))
       

ls_list = list()
distance_list = list()
plot_conns = list()      
mpoints_lon = list()
mpoints_lat = list()

for point in points:
    
    closest_lnsg = np.empty((5))
    closest_lnsg[:] = np.nan
    closest_dist = np.empty((5))
    closest_dist[:] = np.inf
    matchpoints_lon = np.empty((5))
    matchpoints_lon[:] = np.nan
    matchpoints_lat = np.empty((5))
    matchpoints_lat[:] = np.nan
    
    
    #plot
    min_p0 = None
    min_p1 = None
    
    for i, ls in enumerate(linestrings):
        dist, p0, p1 = get_dist(ls, point)
        
        # plot
        if np.less(dist, closest_dist).all():
            min_p0 = p0
            min_p1 = p1
        
        if np.less(dist, closest_dist).any():
            replace_i = np.argmax(closest_dist)
            closest_dist[replace_i] = dist
            closest_lnsg[replace_i] = i
            matchpoints_lon[replace_i] = p0[0]
            matchpoints_lat[replace_i] = p0[1]

    plot_conns.append([min_p0, min_p1])
    #print(closest_dist)
    #print(closest_lnsg)
    ls_list.append(closest_lnsg)
    distance_list.append(closest_dist)
    mpoints_lon.append(matchpoints_lon)
    mpoints_lat.append(matchpoints_lat)
    
print(points[:3])
print(ls_list[:3])
print(distance_list[:3])


df = pd.DataFrame()

df['points'] = points
df['linestring_ids'] = ls_list
df['distance'] = distance_list
pd.set_option('display.max_colwidth', -1)
print(df)

mapped_points = list()

#df['first_pass'] = np.min(df['distance'])

# get closest index
df['i_closest'] = df['distance'].apply(np.argmin)

print(df['distance'])
#print(i_closest)


df['first_pass'] = df.apply(lambda x: x['linestring_ids'][x['i_closest']], axis=1)


print(df['first_pass'])

#df['first_pass'] = df['


# draw closest
converted_ls = list()
for ls in plot_conns:
    #print(map.rev_geocode(ls[0]))
    new_ls = np.array([np.array(map.rev_geocode(p)) for p in ls])
    #print(new_ls)
    if new_ls.size:
        converted_ls.append(new_ls)

# make plot lines
line_segments = LineCollection(converted_ls)


x, y = zip(*(map.rev_geocode((p.x, p.y)) for p in points))
plt.scatter(x, y, c='red', edgecolor='none', s=2, alpha=0.9)

plt.imshow(image)
ax = plt.gca()
ax.add_collection(line_segments)

plt.show()

