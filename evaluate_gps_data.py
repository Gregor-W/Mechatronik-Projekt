#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue June 17 16:48:40 2022

@author: gregor
"""
import matplotlib.pyplot as plt
import mpld3
from mpld3._server import serve
from os.path import exists
import argparse

from Functions.display_map import Map, get_bbox
from Functions.load_data import Ways_Handler, Gps_Handler, get_elevation_list, get_ip, reduce_to
from Functions.map_matching import Matching


# get command line input
parser = argparse.ArgumentParser()
parser.add_argument('gpxfile', metavar='N', type=str, nargs='+',
                    help='gpx-file to evaluate')
args = parser.parse_args()
gpx_file = args.gpxfile[0]


ways_h = Ways_Handler()
gps_h = Gps_Handler()


# load GPX
print("Loading GPX file")
gps_h.load_gpx_file(gpx_file)
print("Found {} GPS-points".format(len(gps_h.points)))

# get bounding box for map
bbox = get_bbox(gps_h.points)
print(bbox)

# check for pickle file for track
if exists(gpx_file + "-ls.plk"):
    print("Loading Linestrings from Pickle")
    ways_h.load_linestrings_pickle(gpx_file + "-ls.plk")
else:
    print("Querying OSM for Linestrings")
    ways_h.query_linestings(bbox)
    ways_h.write_to_pickle(gpx_file + "-ls.plk")


print("Found {} Linestrings".format(len(ways_h.linestrings)))
    
disp_map = Map(bbox=bbox)
matching = Matching(ways_h, gps_h)

print("Map Matching")
matching.map_matching()

print("calculating speeds")
matching.calc_speed("matched_point")


plt.rcParams.update({'font.size': 19})

# plot speeds
fig1 = plt.figure()
plt.title("Speed")
plt.xlabel("GPS point in track")
plt.ylabel("speed in m/s")
fig1.set_size_inches(2 * 6.4, 6)
plt.plot(matching.calc_speed("matched_point"), 'g', label="map matched points")
plt.plot(matching.calc_speed("points"), 'b', label="GPS points")
plt.legend()
         
# plot heights
fig2 = plt.figure()
plt.title("Elevation")
plt.xlabel("GPS point in track")
plt.ylabel("elevation in m")
fig2.set_size_inches(2 * 6.4, 6)
plt.plot(reduce_to(100, gps_h.height), 'b', label="GPS data")
plt.plot(get_elevation_list(matching.get_matched_p(),\
                            'https://api.opentopodata.org/v1/eudem25m')['elevation']\
         , 'g', label="map matched points (OTD)")
plt.plot(get_elevation_list(matching.get_matched_p(),\
                            'https://api.open-elevation.com/api/v1/lookup')['elevation']\
         , 'r', label="map matched points (OE)")
plt.legend()
         

# make map
disp_map.add_linestrings(ways_h.linestrings, 'g')
disp_map.add_linestrings(matching.get_matched_ls(), 'b')
disp_map.add_points(gps_h.points)
fig3 = disp_map.get_fig()
fig3.set_size_inches(2 * 6.4, 2 * 4.8)

# create html for all plots
html1 = mpld3.fig_to_html(fig1)
html2 = mpld3.fig_to_html(fig2)
html3 = mpld3.fig_to_html(fig3)

# serve joined html to browser
serve(html1+html2+html3, ip=get_ip(), port=8889)
#serve(html1+html2+html3, ip='192.168.178.31', port=8889)