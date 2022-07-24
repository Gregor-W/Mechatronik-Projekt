from Functions.display_map import Map
from Functions.load_data import Ways_Handler
from Functions.load_data import Gps_Handler

center = (8.915756, 48.448863)
disp_map = Map(center)
ways_h = Ways_Handler()
gps_h = Gps_Handler()
boxsize = 0.004

# load new ways
if True:
    ways_h.query_linestings(center[0] - boxsize,\
                            center[1] - boxsize,\
                            center[0] + boxsize,\
                            center[1] + boxsize)
    ways_h.write_to_pickle("query_result.plk")

ways_h.load_linestrings_pickle("query_result.plk")
gps_h.load_gpx_file('Test2.gpx')

disp_map.add_linestrings(ways_h.linestrings)
disp_map.add_points(gps_h.points)
disp_map.show_map()