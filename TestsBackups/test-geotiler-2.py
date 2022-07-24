#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 13 12:52:20 2022

@author: gregor
"""
import geotiler
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import pickle as plk
import numpy as np
import gpxpy
import gpxpy.gpx

#center = (9.187204, 48.481309)
center = (8.915756, 48.448863)


#####

# make tile map
map = geotiler.Map(center=(center[0], center[1]), zoom=16, size=(512, 512))
image = geotiler.render_map(map) 

# box size to get roads in
boxsize = 0.001



#####

# load query result form pickle
with open("query_result.plk", "rb") as input_file:
   data = plk.load(input_file)

# get linestring coordinates
linestrings = list()
for way in data.features:
    #print(way)
    linestrings.append(way["geometry"]["coordinates"])

# convert linestrings to plot coordinates
converted_ls = list()
for ls in linestrings:
    #print(map.rev_geocode(ls[0]))
    new_ls = np.array([np.array(map.rev_geocode(p)) for p in ls])
    print(new_ls)
    if new_ls.size:
        converted_ls.append(new_ls)

print(converted_ls[0])
#print(np.array(converted_ls))

# make plot lines
line_segments = LineCollection(converted_ls, linestyle='solid')

plt.imshow(image)
ax = plt.gca()
ax.add_collection(line_segments)

plt.show()