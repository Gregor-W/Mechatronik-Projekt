import numpy as np
import gpxpy
import gpxpy.gpx


class Ways_Handler:
    linestrings = list()
    last_pickle = None

    def query_linestings(self, lat_min, lon_min, lat_max, lon_max):
        query = """way["highway"]({}, {}, {}, {});out geom;""".format(lon_min,\
                                                                      lat_min,\
                                                                      lon_max,\
                                                                      lat_max)
        api = overpass.API()
        data = api.get(query)
        
        for way in data.features:
            self.linestrings.append(way["geometry"]["coordinates"])
    
    def write_to_pickle(self, pickle_file):
        with open(pickle_file, "wb") as output_file:
            plk.dump(data, self.linestrings)
        self.last_pickle = pickle_file
    
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

def load_gpx_file(file):
    # get gpx points
    gpx_file = open(file, 'r')

    gpx = gpxpy.parse(gpx_file)

    points = list()

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append(Point(point.longitude, point.latitude))
    return points
