#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 16 12:58:33 2022

@author: gregor
"""

import geotiler
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import pickle as plk
import numpy as np
import gpxpy
import gpxpy.gpx


center = (8.915756, 48.448863)



#####

# make tile map
map = geotiler.Map(center=(center[0], center[1]), zoom=16, size=(512, 512))
image = geotiler.render_map(map)


# Parsing an existing file:
# -------------------------

gpx_file = open('Test2.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

points = list()

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
            points.append((point.longitude, point.latitude))

for waypoint in gpx.waypoints:
    print('waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude))

for route in gpx.routes:
    print('Route:')
    for point in route.points:
        print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))

x, y = zip(*(map.rev_geocode(p) for p in points))
plt.scatter(x, y, c='red', edgecolor='none', s=5, alpha=0.9)
plt.imshow(image)

plt.show()