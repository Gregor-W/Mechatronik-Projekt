#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 17:11:01 2022

@author: gregor
"""
import numpy as np
import gpxpy
import gpxpy.gpx
import overpass
import pickle as plk
from shapely.geometry import Point, LineString
from requests import get
import pandas as pd
import socket

# Class to provide gpx data
class Gps_Handler:
    points = list()
    times = list()
    height = list()
    # load gps points from gpx file
    def load_gpx_file(self, file):
        # open gpx
        with open(file, 'r') as gpx_file:

            gpx = gpxpy.parse(gpx_file)

        # get all gps points
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    self.points.append(Point(point.longitude, point.latitude))
                    self.times.append(point.time)
                    self.height.append(point.elevation)
                    

# Class to deal with way linestrings, querying and saving to file
class Ways_Handler:
    linestrings = list()
    bboxes = list()
    last_pickle = None
    
    # query all ways in box with corners
    def query_linestings(self, bbox):
        query = """way["highway"]({}, {}, {}, {});out geom;""".format(bbox[1], bbox[0], bbox[3], bbox[2])
        api = overpass.API()
        data = api.get(query)
        print("Overpass-Query: {}".format(query))
        # get linestrings
        for way in data.features:
            if not way["geometry"]["coordinates"]:
                continue
            self.linestrings.append(LineString(way["geometry"]["coordinates"]))
    
    # write ways to pickle
    def write_to_pickle(self, pickle_file):
        with open(pickle_file, "wb") as output_file:
            plk.dump(self.linestrings, output_file)
        self.last_pickle = pickle_file
    
    # load ways from pickle
    def load_linestrings_pickle(self, pickle_file = None):
        if pickle_file is not None:
            # load query result form pickle
            with open(pickle_file, "rb") as input_file:
               self.linestrings = plk.load(input_file)
        elif self.last_pickle is not None:
            # load query result form pickle
            with open(self.last_pickle, "rb") as input_file:
               self.linestrings = plk.load(input_file)
        else:
            raise Exception("No pickle file found")

url_opentopodata = 'https://api.opentopodata.org/v1/eudem25m' # max 100
url_openelevation = 'https://api.open-elevation.com/api/v1/lookup'

def get_elevation_list(points, url):
    '''
        script for returning elevation in m from lat, long
    '''
    if points is None: return None
    
    points = reduce_to(100, points)
        
    #if len(points) > 100:
        # split into groups of 100
        #n = 100
        #point_lists = [points[i:i + n] for i in range(0, len(points), n)]
        #all_elevation = pd.Series()
        #for ps in point_lists:
        #    new_elevations = get_elevation_list(ps, url)
        #    if new_elevations is None:
        #        print("could not get all elevations")
        #        return None
        #    all_elevation = pd.concat([all_elevation, new_elevations],\
        #                              ignore_index=True)
        #return all_elevation

    query = f'?locations='

    # build query, lat/lon switched
    for p in points[:-1]:
        query += f'{p.y},{p.x}|'
    
    query += f'{points[-1].y},{points[-1].x}'

    full_query = (url + query)
    
    print("Elevation-Query: {}".format(full_query))
    
    # Request with a timeout for slow responses
    r = get(full_query, timeout = 20)

    # Only get the json response in case of 200 or 201
    if r.status_code == 200 or r.status_code == 201:
        elevation = pd.json_normalize(r.json(), 'results')
    else: 
        elevation = None
    return elevation
    
# reduce list to l elements with the same distance between elements
def reduce_to(x, l):
    i = 0
    length = len(l)
    while length > x:
        i += 1
        length = len(l) / i
    
    r_l= np.array(l, dtype=object)
    if i != 0:
        r_l = r_l[::i] 
    return r_l

# returns local ip
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
