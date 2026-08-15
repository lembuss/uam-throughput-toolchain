# all parameters assumed in the study
import functions


class eVTOL:
    cruise_altitude_ft = 2500 # cruising altitude for evtol is 1000ft above ground distance
    cruise_velocity_kmh = 120 # cruise velocity in km/h 
    initial_approach_segment_nm = 4 # segment in nm
    intermediate_approach_segment_nm = 3 # segment in nm 
    final_approach_segment_m = 2412 # segment in m 
    mapt_altitude_ft = 1986 #MAPt altitude in ft
    RF_turn_radius_m = 1250 # turn radius between intermediate and inital segments in m
    holding_straight_segment_m =  2000 # straight segment in m
    holding_turn_radius_m = 700 # turn radius in m
    holding_altitude_ft = 2500 #MAPt altitude in ft
    
class Traffic: # aircraft traffic characteristics
    # regulatory considerations
    glideslope_angle_deg = 3.0  # Glide slope angle in degrees
    ntz_distance_m = 610 # retrieved from Reinisch
    noz_distance_m = 540 # retrieved from Reinisch
    radar_separation_nm = 3 # radar separation in 3 NM 
    rwy_centerline_separation_m = 1150

    # vehicle characteristics
    cruise_velocity_knots = 150 # cruise velocity in knots

    # altitudes and segment info from DFS chart for glideslope
    final_approach_fix_altitude_ft = 5000 # Altitude at the starting point in feet
    runway_elevation_ft = 1470      # may get overriden - used for glideslope   
    start_separation_minima_altitude_ft = eVTOL.cruise_altitude_ft + 1000
    end_separation_minima_altitude_ft = eVTOL.cruise_altitude_ft
    

    final_approach_segment_nm = 11.1 # may be overriden later  
    

