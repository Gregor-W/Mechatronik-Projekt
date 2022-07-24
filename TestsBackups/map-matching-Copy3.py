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
    
    

def find_best_ls(first_i, prev_i, next_i, linestring_ids, distance):

    if first_i == prev_i or first_i == next_i:
        return first_i
    
    max_dist = 6
    
    # get distance to other linestrings
    prev_dist = None
    next_dist = None
    for e, ls in enumerate(linestring_ids):
        if prev_i == ls:
            prev_dist = distance[e]
        if next_i == ls:
            next_dist = distance[e]
    
    if next_dist is None or prev_dist is None:
        return first_i
    
    print("something usefull")
    
    if next_dist is None and prev_dist < max_dist:
        return prev_i
    
    if prev_dist is None and next_dist < max_dist:
        return next_i
    
    if prev_dist < next_dist and prev_dist < max_dist:
        return prev_i
    if next_dist < prev_dist and next_dist < max_dist:
        return next_i
    
    
#####
# get all ways
# load query result form pickle
with open("query_result.plk", "rb") as input_file:
   linestrings = plk.load(input_file)

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
    # distance and linestring id
    closest_dist = np.empty((5))
    closest_dist[:] = np.inf
    closest_lnsg = np.empty((5))
    closest_lnsg[:] = np.nan
    
    # matched points
    matchpoints_lon = np.empty((5))
    matchpoints_lon[:] = np.nan
    matchpoints_lat = np.empty((5))
    matchpoints_lat[:] = np.nan
    
    lists = [closest_dist, closest_lnsg, matchpoints_lon, matchpoints_lat]

    for i, ls in enumerate(linestrings):
        dist, p0, p1 = get_dist(ls, point)
        data = [dist, i, p0[0], p0[1]]
        if dist > 20:
            continue
        # get id in sorted array
        idx = closest_dist.searchsorted(dist)
        # insert data into arrays
        if idx < 4:
            for l, d in zip(lists, data):
                l[:] = np.concatenate((l[:idx], [d], l[idx:-1]))
        elif idx == 4:
            for l, d in zip(lists, data):
                l[-1] = d

    ls_list.append(closest_lnsg)
    distance_list.append(closest_dist)
    mpoints_lon.append(matchpoints_lon)
    mpoints_lat.append(matchpoints_lat)

df = pd.DataFrame()

df['points'] = points
df['linestring_ids'] = ls_list
df['distance'] = distance_list
df['ls_lon'] = mpoints_lon
df['ls_lat'] = mpoints_lat

pd.set_option('display.max_colwidth', None)
print(df)

mapped_points = list()

# get closest index
#df['i_closest'] = df['distance'].apply(np.argmin)
#print(df['i_closest'])

df['first_pass'] = df.apply(lambda x: x['linestring_ids'][0], axis=1)
print(df['first_pass'])

first = df['first_pass'].iloc[0]
last = df['first_pass'].iloc[-1]
df['fp_prev'] = df['first_pass'].shift(1, fill_value=first)
df['fp_next'] = df['first_pass'].shift(-1, fill_value=last)

df['second_pass'] = df.apply(lambda x: find_best_ls(x['first_pass'],\
                                                    x['fp_prev'],\
                                                    x['fp_next'],\
                                                    x['linestring_ids'],\
                                                    x['distance']), axis=1)


df['p_lon'] = df.apply(lambda x: x['ls_lon'][0] if x['distance'][0] < 12 else x['points'].x, axis=1)
df['p_lat'] = df.apply(lambda x: x['ls_lat'][0] if x['distance'][0] < 12 else x['points'].y, axis=1)


for p, lon, lat in zip(df['points'], df['p_lon'], df['p_lat']):
    plot_conns.append([p, Point(lon, lat)])

# draw closest
converted_ls = list()
for double_point in plot_conns:

    new_ls = [map.rev_geocode((p.x, p.y)) for p in double_point]
    #print(new_ls)
    converted_ls.append(new_ls)

# make plot lines
line_segments = LineCollection(converted_ls)


x, y = zip(*(map.rev_geocode((p.x, p.y)) for p in points))
plt.scatter(x, y, c='red', edgecolor='none', s=2, alpha=0.9)

plt.imshow(image)
ax = plt.gca()
ax.add_collection(line_segments)

plt.show()

