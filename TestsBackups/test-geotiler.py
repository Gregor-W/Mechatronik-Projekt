#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 17:11:01 2022

@author: gregor
"""
#import nest_asyncio
#nest_asyncio.apply()

import geotiler
import overpy
import overpass
import matplotlib.pyplot as plt
import pickle as plk


center = (8.915756, 48.448863)
#center = (9.187204, 48.481309)

map = geotiler.Map(center=(center[0], center[1]), zoom=16, size=(512, 512))

image = geotiler.render_map(map) 


boxsize = 0.004

query = """[out:json][timeout:25];(way["highway"]({}, {}, {}, {});out;""".format(center[0] - boxsize,\
                                                                                 center[1] - boxsize,\
                                                                                 center[0] + boxsize,\
                                                                                 center[1] + boxsize)

print(query)
    
#query = """way["name"="Gielgenstraße"](50.7,7.1,50.8,7.25);out;"""
query = """way["highway"]({}, {}, {}, {});out geom;""".format(center[1] - boxsize,\
                                                         center[0] - boxsize,\
                                                         center[1] + boxsize,\
                                                         center[0] + boxsize)
    
"""
# Overpy
api = overpy.Overpass()

print(query)

# run query    
result = api.query(query)
print(result)
print(len(result.nodes))
print(len(result.ways))
print(result.ways[0])

# get first way and nodes
way = result.ways[0]
way.get_nodes(resolve_missing=True)

# get coords
print(way)
print(way.nodes)
print(way.nodes[0].lat)

print(result.ways[0])
all_ways = list()

# get all nodes
#ways = result.ways
#for way in ways:
#    way.get_nodes(resolve_missing=True)
#    line = list()
#    for node in way.nodes:
#        line.append((node.lat, node.lon))


print(all_ways[0:10])      
"""
# other overpass api
api = overpass.API()
data = api.get(query)    

with open("query_result.plk", "wb") as output_file:
    plk.dump(data, output_file)

print(type(data))
print(data[0])
print(data[0]["geometry"])
print(data[0]["geometry"]["coordinates"][0])
linestrings = list()
for way in data.features:
    #print(way)
    linestrings.append(way["geometry"]["coordinates"])

print(linestrings[0:10])






#
# plot custom points
#e
#x0, y0 = 9.187204, 48.481309 # http://www.openstreetmap.org/search?query=46.48114%2C11.78816
#x1, y1 = 9.187000, 48.481000 # http://www.openstreetmap.org/search?query=46.48165%2C11.78771

x0, y0 = center[0] - boxsize, center[1] - boxsize
x1, y1 = center[0] + boxsize, center[1] + boxsize

points = ((x0, y0), (x1, y1))
x, y = zip(*(map.rev_geocode(p) for p in points))
plt.scatter(x, y, c='red', edgecolor='none', s=10, alpha=0.9)

plt.imshow(image)
plt.show()