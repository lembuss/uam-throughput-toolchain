import simplekml
import Misc_Test_Scripts.variables as variables
import math
from datetime import datetime, timedelta
from geopy.distance import geodesic
import numpy as np

def calculate_bearing(start, end):
    # Convert latitude and longitude from degrees to radians
    lat1, long1 = start
    lat2, long2 = end

    lat1 = math.radians(lat1)
    long1 = math.radians(long1)
    lat2 = math.radians(lat2)
    long2 = math.radians(long2)

    # Calculate the difference in longitudes
    dLong = long2 - long1

    # Calculate the bearing
    x = math.sin(dLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dLong))
    bearing = math.atan2(x, y)

    # Convert bearing from radians to degrees
    bearing = math.degrees(bearing)

    # Normalize the bearing
    bearing = (bearing + 360) % 360

    return bearing

def calculate_intermediate_points(start, end, distance_increment):
    # Calculate the total distance between start and end points
    total_distance = geodesic(start, end).kilometers

    # Calculate the bearing between the start and end points
    bearing = calculate_bearing(start, end)

    # Calculate the number of segments
    num_segments = int(total_distance // distance_increment)

    # List to store all points including start and end
    points = [start]

    for i in range(1, num_segments):
        # Calculate the intermediate point
        fraction = i / num_segments
        intermediate_point = geodesic().destination(start, bearing, distance_increment * i).format_decimal()
        # convert to tuple
        if isinstance(intermediate_point, str):
            lat, lon = intermediate_point.split(', ')
            intermediate_point = (float(lat)),(float(lon))
            points.append(intermediate_point)
        else:
            points.append(intermediate_point)
            
    points.append(end)  # Add the end point

    return points

# Define your start, end points and distance increment
start_point = variables.Messe
end_point = variables.IAF_08_South
distance_increment = 5  # in kilometers

# Calculate intermediate points
waypoints = calculate_intermediate_points(start_point, end_point, distance_increment)

# Create a KML object for waypoints
waypoints_kml = simplekml.Kml()

# Switch latitude and longitude for each waypoint because of kml format
waypoints = [(lon, lat) for lat, lon in waypoints]

# Add each waypoint to the KML
for idx, waypoint in enumerate(waypoints):
    waypoints_kml.newpoint(name=f"Waypoint {idx+1}", coords=[waypoint])

# Save the KML file
waypoints_kml.save("waypoints.kml")

# Create a KML object for the path
path_kml = simplekml.Kml()

# Time-related variables
start_time = datetime(2023, 1, 1, 12, 0, 0)
vehicle_speed = 120 * 1.852 # km/h
time_increment = timedelta(hours=distance_increment/vehicle_speed)  # Increment time for each segment

# Create the time-animated segments
for i in range(1, len(waypoints)):
    segment = path_kml.newlinestring()
    segment.coords = [waypoints[i - 1], waypoints[i]]
    segment.timestamp.when = (start_time + i * time_increment).isoformat()

# Save the KML file
path_kml.save("evtol_trajectory_path.kml")