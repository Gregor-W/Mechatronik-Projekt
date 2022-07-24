#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 17 16:48:40 2022

@author: gregor
"""


import numpy as np
import pandas as pd
import datetime

from geopy.distance import geodesic
from geopy.distance import great_circle

from pyproj import Geod
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points



# class for map matching
class Matching:
    ways_handler = None
    df = pd.DataFrame()
    
    def __init__(self, wh, gps_handler):
        self.df['points'] = gps_handler.points
        self.df['time']   = pd.to_datetime(gps_handler.times)
        self.df['height'] = gps_handler.height
        self.ways_handler = wh

    # Get distance between Linestring and Coords in meters
    @staticmethod
    def get_ls_dist_m(ls, point):
        #if point.distance(ls) > 20:
        #    return np.nan, None, None
        
        # get closest point on ls
        np = nearest_points(ls, point)
        # get distance to linestring
        dist = geodesic((np[0].x, np[0].y), (np[1].x, np[1].y)).m
        #dist = np[0].distance(np[1])
        return dist, (np[0].x, np[0].y), (np[1].x, np[1].y)
    
    # Get distance between Points in meters
    @staticmethod
    def get_dist_m(p0, p1):
        if np.isnan(p0).any() or np.isnan(p1).any():
            return None
        dist = geodesic((p0.x, p0.y), (p1.x, p1.y)).m
        return dist
        
    # Smarter matching
    @staticmethod
    def find_best_ls(df):
        
        first_i = df['first_pass']
        prev_i = df['fp_prev']
        next_i  = df['fp_next']
        linestring_ids = df['linestring_ids']
        distance = df['distance']
        
        # if other points have the same linestring
        if first_i == prev_i or first_i == next_i:
            return first_i

        max_dist = 20

        # get distance to other linestrings
        prev_dist = None
        next_dist = None
        for e, ls in enumerate(linestring_ids):
            if prev_i == ls:
                prev_dist = distance[e]
            if next_i == ls:
                next_dist = distance[e]

        if next_dist is None and prev_dist is None:
            return first_i

        print("changed linestring")
        # map to different linestring
        if next_dist is None and prev_dist < max_dist:
            return prev_i
        if prev_dist is None and next_dist < max_dist:
            return next_i

        if prev_dist < next_dist and prev_dist < max_dist:
            return prev_i
        if next_dist < prev_dist and next_dist < max_dist:
            return next_i
        
    # get closest linestring mapped point with datafram
    @staticmethod
    def select_points_old(df):
        if df['distance'][0] < 20:
            return Point(df['ls_lon'][0], df['ls_lat'][0])
        else:
            return df['points']
    
    # get map matched point with dataframe
    @staticmethod
    def select_points(df):
        i = np.where(df['linestring_ids'] == df['second_pass'])[0]
        
        if df['distance'][i] < 20:
            return Point(df['ls_lon'][0], df['ls_lat'][0])
        else:
            return df['points']
    
    # calculate speed on dataframe
    @staticmethod
    def get_speed(df):
        # get distances
        dist0 = Matching.get_dist_m(df['current_point'], df['prev_point'])
        dist1 = Matching.get_dist_m(df['current_point'], df['next_point'])
        # get time deltas
        time0 = df['delta_t_prev']
        time1 = df['delta_t_next']
        if time0 == 0 or time1 == 0:
            return None
        # calc average
        return (dist0 / time0 + dist1 / time1) / 2
    
    # get 5 closes map matched points, distance, linestrings
    def get_closest_linestrings(self, point):
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
        
        # arrays to fill
        lists = [closest_dist, closest_lnsg, matchpoints_lon, matchpoints_lat]
        
        # for every linestring
        for i, ls in enumerate(self.ways_handler.linestrings):
            dist, p0, p1 = self.get_ls_dist_m(ls, point)
            data = [dist, i, p0[0], p0[1]]
            if np.isnan(dist):
                continue
            
            if dist > closest_dist[-1]:
                continue
            
            # get index in array for new distance
            idx = closest_dist.searchsorted(dist)
            # insert data into arrays
            if idx < 4:
                for l, d in zip(lists, data):
                    l[:] = np.concatenate((l[:idx], [d], l[idx:-1]))
            elif idx == 4:
                for l, d in zip(lists, data):
                    l[-1] = d

        return closest_lnsg, closest_dist, matchpoints_lon, matchpoints_lat

    # map match
    def map_matching(self):
        # get map match array columns
        self.df['linestring_ids'],\
        self.df['distance'],\
        self.df['ls_lon'],\
        self.df['ls_lat'] = zip(*(self.df['points'].apply(self.get_closest_linestrings)))

        pd.set_option('display.max_colwidth', None)
        #print(self.df)
        
        # first pass, get closest distance
        self.df['first_pass'] = self.df.apply(lambda x: x['linestring_ids'][0], axis=1)
        #print(self.df['first_pass'])
        
        first = self.df['first_pass'].iloc[0]
        last = self.df['first_pass'].iloc[-1]
        self.df['fp_prev'] = self.df['first_pass'].shift(1, fill_value=first)
        self.df['fp_next'] = self.df['first_pass'].shift(-1, fill_value=last)
        
        # select other linestring if no close points are on the same
        self.df['second_pass'] = self.df.apply(self.find_best_ls, axis=1)
        
        # make Point objects of mmed points 
        self.df['matched_point'] = self.df.apply(self.select_points, axis=1)
        
    # calculate speed on dataframe
    def calc_speed(self, column):
        # shift columns for speed calcs
        self.df['current_point'] = self.df[column]
        self.df['prev_point'] = self.df[column].shift(1, fill_value=np.nan)
        self.df['next_point'] = self.df[column].shift(-1, fill_value=np.nan)
        
        first = self.df['time'].iloc[0]
        self.df['prev_time']  = self.df['time'].shift(1, fill_value=first)
        last = self.df['time'].iloc[-1]
        self.df['next_time']  = self.df['time'].shift(-1, fill_value=last)
        
        
        self.df['delta_t_prev'] = (self.df['time'] - self.df['prev_time']).dt.total_seconds()
        self.df['delta_t_next'] = (self.df['next_time'] - self.df['time']).dt.total_seconds()
        
        # calcualte speed
        self.df['speed'] = self.df.apply(self.get_speed, axis=1)
        return self.df['speed']
    
    # create linestrings between point and mmed point
    def get_matched_ls(self):
        plot_conns = list()
        for p, p2 in zip(self.df['points'], self.df['matched_point']):
            plot_conns.append([p, p2])
        return plot_conns
    
    # get mmed points
    def get_matched_p(self):
        return self.df['matched_point'].tolist()



