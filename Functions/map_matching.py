#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 17 16:48:40 2022

@author: gregor
"""
import time

import numpy as np
import pandas as pd
import datetime

from geopy.distance import geodesic
from geopy.distance import great_circle

#from pyproj import Geod
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points

test_mark_points = list()

# class for map matching
class Matching:
    ways_handler = None
    df = pd.DataFrame()
    max_dist_mm = 15
    
    # Get all data in init
    def __init__(self, wh, gps_handler):
        self.df['points'] = gps_handler.points
        self.df['time']   = pd.to_datetime(gps_handler.times)
        self.df['height'] = gps_handler.height
        self.ways_handler = wh

    # Get distance and closest point between Linestring and Coords in meters
    @staticmethod
    def get_ls_dist(ls, point):
        np = nearest_points(ls, point)
        dist = np[0].distance(np[1])
        return dist, np[0], np[1]
    
    # Get distance between Points in meters
    @staticmethod
    def get_dist_m(p0, p1):
        if np.isnan(p0).any() or np.isnan(p1).any():
            return None
        dist = geodesic((p0.x, p0.y), (p1.x, p1.y)).m
        return dist
        
    # Smarter matching, fixing some wrong matches
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

        # get distance to other linestrings
        prev_dist = None
        next_dist = None
        # distance to other possible linestrings
        for e, ls in enumerate(linestring_ids):
            if prev_i == ls:
                prev_dist = distance[e]
            if next_i == ls:
                next_dist = distance[e]

        if next_dist is None and prev_dist is None:
            return first_i

        # map to closest different linestring
        if next_dist is None and prev_dist < Matching.max_dist_mm:
            return prev_i
        if prev_dist is None and next_dist < Matching.max_dist_mm:
            return next_i
        if prev_dist <= next_dist and prev_dist < Matching.max_dist_mm:
            return prev_i
        if next_dist < prev_dist and next_dist < Matching.max_dist_mm:
            return next_i
        
    # get map matched point with dataframe
    @staticmethod
    def select_points(df):
        i = np.where(df['linestring_ids'] == df['second_pass'])[0]
        # check if point was mapmatched (could be to far from any way)
        if df['distance'][i] < Matching.max_dist_mm:
            return df['mm_points'][i][0]
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
    
    
    # calculate correct distance on dataframe
    @staticmethod
    def correct_dist(df):
        p = df['points']
        mm_ps = df['mm_points']
        # calc correct
        new_dist = np.array([Matching.get_dist_m(p, p2) for p2 in mm_ps])
        return new_dist
    
    # get 5 closes map matched points, distance, linestrings
    def get_closest_linestrings(self, point):
        # distance and linestring id
        closest_dist = np.empty((5))
        closest_dist[:] = np.inf
        closest_lnsg = np.empty((5))

        # matched points
        matchpoints = np.empty((5), dtype=object)

        # arrays to fill
        lists = [closest_dist, closest_lnsg, matchpoints]
        
        # for every linestring
        for i, ls in enumerate(self.ways_handler.linestrings):
            dist, p0, p1 = self.get_ls_dist(ls, point)
            data = [dist, i, p0]
            if np.isnan(dist):
                continue
            
            if dist > closest_dist[-1]:
                continue
            
            # get index in array for new distance
            idx = closest_dist.searchsorted(dist)
            # insert data into arrays, depending on new position
            if idx < 4:
                for l, d in zip(lists, data):
                    l[:] = np.concatenate((l[:idx],\
                                           np.array([d], dtype=object),\
                                           l[idx:-1]))
            elif idx == 4:
                for l, d in zip(lists, data):
                    l[-1] = d

        return closest_lnsg, closest_dist, matchpoints
    
    # map match
    def map_matching(self):
        start = time.time()
        # get map match array columns
        self.df['linestring_ids'],\
        self.df['distance'],\
        self.df['mm_points'] = zip(*(self.df['points'].apply(self.get_closest_linestrings)))
        
        # correct the distances
        self.df['distance'] = self.df.apply(self.correct_dist, axis=1)
        end = time.time()
        print("time for mm: {}".format(end - start))
        
        #pd.set_option('display.max_colwidth', None)
        #print(self.df)
        
        # first pass, get closest distance
        self.df['first_pass'] =\
            self.df.apply(lambda x:\
                              x['linestring_ids'][np.argmin(x['distance'])]\
                          , axis=1)
        
        first = self.df['first_pass'].iloc[0]
        last = self.df['first_pass'].iloc[-1]
        
        shift = 2
        
        self.df['fp_prev'] = self.df['first_pass'].shift(shift, fill_value=first)
        self.df['fp_next'] = self.df['first_pass'].shift(-shift, fill_value=last)
        
        # select other linestring if no close points are on the same
        self.df['second_pass'] = self.df.apply(self.find_best_ls, axis=1)
        
        # make Point objects of mmed points 
        self.df['matched_point'] = self.df.apply(self.select_points, axis=1)
        
    # calculate speed on dataframe
    def calc_speed(self, column):
        # shift point columns for speed calcs
        self.df['current_point'] = self.df[column]
        self.df['prev_point'] = self.df[column].shift(1, fill_value=np.nan)
        self.df['next_point'] = self.df[column].shift(-1, fill_value=np.nan)
        # shift time columns for speed calcs
        first = self.df['time'].iloc[0]
        self.df['prev_time']  = self.df['time'].shift(1, fill_value=first)
        last = self.df['time'].iloc[-1]
        self.df['next_time']  = self.df['time'].shift(-1, fill_value=last)
        
        # time diff
        self.df['delta_t_prev'] = (self.df['time'] - self.df['prev_time']).dt.total_seconds()
        self.df['delta_t_next'] = (self.df['next_time'] - self.df['time']).dt.total_seconds()
        
        # calcualte speed
        self.df['speed'] = self.df.apply(self.get_speed, axis=1)
        return self.df['speed']
    
    # create linestrings between point and mmed point for visualisation
    def get_matched_ls(self):
        plot_conns = list()
        for p, p2 in zip(self.df['points'], self.df['matched_point']):
            plot_conns.append([p, p2])
        return plot_conns
    
    # get mmed points as list
    def get_matched_p(self):
        return self.df['matched_point'].tolist()

        