from requests import get
from pandas import json_normalize
import pandas as pd
import numpy as np

import geotiler
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import pickle as plk
import gpxpy
import gpxpy.gpx

from shapely.geometry import Point, LineString
from shapely.ops import nearest_points

# get elevation of single point
def get_elevation(lat = None, long = None):
    '''
        script for returning elevation in m from lat, long
    '''
    if lat is None or long is None: return None
    
    query = ('https://api.open-elevation.com/api/v1/lookup'
             f'?locations={lat},{long}')
    
    # Request with a timeout for slow responses
    r = get(query, timeout = 20)

    # Only get the json response in case of 200 or 201
    if r.status_code == 200 or r.status_code == 201:
        elevation = json_normalize(r.json(), 'results')
    else: 
        elevation = None
    return elevation

# get elevation of multiple points
def get_elevation_list(points, query_url):
    '''
        script for returning elevation in m from lat, long
    '''
    if points is None: return None
    

    query = f'?locations='
    
    # build query
    for p in points[:-1]:
        query += f'{p.x},{p.y}|'
    
    query += f'{points[-1].x},{points[-1].y}'
    
    #print(query)
    
    full_query = (query_url + query)
    
    # Request with a timeout for slow responses
    r = get(full_query, timeout = 20)

    # Only get the json response in case of 200 or 201
    if r.status_code == 200 or r.status_code == 201:
        elevation = json_normalize(r.json(), 'results')
    else: 
        elevation = None
    return elevation

# small amount of points test
center = (8.915756, 48.448863)
print("###")
#print(get_elevation(center[0], center[1]))

points = np.array([Point(8.915756, 48.448863), Point(1, 2), Point(2, 3)])

#print(get_elevation_list(points))


            
#####
# get gpx points
gpx_file = open('Test2.gpx', 'r')

gpx = gpxpy.parse(gpx_file)

points = list()
elevations = list()

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            points.append(Point(point.latitude, point.longitude))
            elevations.append(point.elevation)

print("Amount GPX points: {}".format(len(points)))

#points = np.array([Point(57.688709,11.976404), Point(56,123)])


query_url = 'https://api.opentopodata.org/v1/eudem25m' # max 100
query_url2 = 'https://api.open-elevation.com/api/v1/lookup'

elevations2 = get_elevation_list(points, query_url)
elevations3 = get_elevation_list(points, query_url2)


with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    print()

print(elevations)
print(elevations2)
print(elevations3)

plt.plot(elevations)
plt.plot(elevations2['elevation'])
plt.plot(elevations3['elevation'])
plt.show()