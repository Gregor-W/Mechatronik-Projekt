#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 17:11:01 2022

@author: gregor
"""
import geotiler
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from shapely.geometry import Point, LineString
import socket

# class to display map
class Map:
    display_map = None
    linestrings = list()
    colors = list()
    x = list()
    y = list()
    
    def __init__(self, center=None, bbox=None):
        # map centered on point with fixed size
        if center:
            self.display_map = geotiler.Map(center=center, zoom=16, size=(512, 512))
        # map according to bbox
        if bbox:
            self.display_map = geotiler.Map(extent=bbox, zoom=16)
    
    # add linestrings to the map
    def add_linestrings(self, linestring_list, color):
        new_ls_count = 0
        # for linestrings as LineString objects
        if isinstance(linestring_list[0], LineString):
            for ls in linestring_list:
                if not ls:
                    continue
                new_ls = [self.display_map.rev_geocode((p)) for p in zip(ls.coords.xy[0],\
                                                                         ls.coords.xy[1])]
                self.linestrings.append(new_ls)
                new_ls_count += 1
        # for linestrings as lists of Points objects
        elif isinstance(linestring_list[0][0], Point):
            for ls in linestring_list:
                if not ls:
                    continue
                new_ls = [self.display_map.rev_geocode((p.x, p.y)) for p in ls]
                self.linestrings.append(new_ls)
                new_ls_count += 1
        # for linestrings as list of tuples
        else:
            for ls in linestring_list:
                if not ls:
                    continue
                new_ls = [self.display_map.rev_geocode(p) for p in ls]
                self.linestrings.append(new_ls)
                new_ls_count += 1
        # add colors for all linestrings 
        self.colors += [color] * new_ls_count
         
    # add points to map
    def add_points(self, point_list):
        if isinstance(point_list[0], Point):
            x, y = zip(*(self.display_map.rev_geocode((p.x, p.y)) for p in point_list))
        else:
            x, y = zip(*(self.display_map.rev_geocode(p) for p in point_list))
        self.x.append(x)
        self.y.append(y)
        
    def show_map(self):
        self.get_fig()
        plt.show()
        
    # returns map with features as plt figure
    def get_fig(self):
        image = geotiler.render_map(self.display_map) 
        line_segments = LineCollection(self.linestrings,\
                                       color=self.colors,\
                                       linestyle='solid',
                                       linewidths=5)
        
        fig = plt.figure()
        #plt.scatter(self.x, self.y, c='red', edgecolor='none', s=30, alpha=0.9, zorder=10)
        plt.scatter(self.x, self.y, c='red', edgecolor='none', s=0.5, alpha=0.9, zorder=10)
        plt.imshow(image)
        ax = plt.gca()
        ax.add_collection(line_segments)
        return fig
    
# get outer bbox for list of points
def get_bbox(points):
    min_lat, min_lon, max_lat, max_lon = None, None, None, None

    for p in points:
        if min_lon is None or min_lon > p.x:
            min_lon = p.x
        if min_lat is None or min_lat > p.y:
            min_lat = p.y
        if max_lon is None or max_lon < p.x:
            max_lon = p.x
        if max_lat is None or max_lat < p.y:
            max_lat = p.y
    bd = 0.0005
    return min_lon - bd, min_lat - bd, max_lon + bd, max_lat +bd

        
