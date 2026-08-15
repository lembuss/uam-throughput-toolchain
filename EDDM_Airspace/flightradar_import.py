# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 15:42:40 2023

@author: brian
"""

from FlightRadar24 import FlightRadar24API

"""
# create instance
fr_api = FlightRadar24API()

# get flights list 
flights = fr_api.get_flights()

# get airports list
airports = fr_api.get_airports()

# get airlines list
airlines = fr_api.get_airlines()

# zones
zones = fr_api.get_zones()

# flight details - ETA, trail, aircraft details
flight = ** - need to find out how to create flight instance
flight_details =fr_api.get_flight_details(flight)
flight = set_flight_details(flight_details)

# airport details - runways, temperarture, arrivals etc
airport = ** - need to find out how to create airport instance
airport_details = fr_api.get_airport_details(airport.icao)

# get distance between flight and airport
airport = fr_api.get_airport("<airport_code>")
distance  flight.get_distance_from(airport)

# realtime tracker parameters
flight_tracker = fr_api.get_flight_tracker_config()
flight_tracker.limit = 10

fr_api.set_flight_tracker_config(flight_tracker,...)

flights = fr_api.get_flights(..)

"""
fr_api = FlightRadar24API()

flight_tracker = fr_api.get_flight_tracker_config()
flight_tracker.limit = 10

fr_api.set_flight_tracker_config(flight_tracker)

flights = fr_api.get_flights()