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
    np = nearest_points(ls, Point(point[0], point[1]))
    
    dist = np.distance(point)
    
    return np.array(dist, np[0].x, np[0].y, np[1].x, np[1].y)
    


def get_closest_linestrings(point, linestrings):
    amount = 3
    
    for i, ls in enumerate(linestrings):
        dist, p0, p1 = get_dist(ls, point)
        
    return closest


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


print(vget_dist(linestrings, points[0]))

df = pd.DataFrame()

df['points'] = points
df['']


