import os
import random
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import functions
from parameters import Traffic, eVTOL
import approach
import aircraft_categories
import trajectory_design 


def determine_traffic_approach_class(active_runway):
    traffic_approach_class = functions.find_child_with_attribute(approach.TrafficApproach,
                                                      active_runway, 
                                                      'runway' # attribute value
    )
    return traffic_approach_class

def determine_evtol_approach_class(traffic_approach):

    if isinstance(traffic_approach, approach.Approach26L):
        evtol_approach_class = approach.Approach26CSouth
    elif isinstance(traffic_approach, approach.Approach26R):
        evtol_approach_class = approach.Approach26CNorth
    if isinstance(traffic_approach, approach.Approach08L):
        evtol_approach_class = approach.Approach08CNorth
    elif isinstance(traffic_approach, approach.Approach08R):
        evtol_approach_class = approach.Approach08CSouth
    
    return evtol_approach_class

def determine_aircraft_position(ref_distance_nm):
    aircraft_altitude_ft = functions.calculate_altitude_glideslope_ft(traffic_approach.runway_elevation_ft,
                                                                      ref_distance_nm,
                                                                      Traffic.glideslope_angle_deg)
    
    aircraft_altitude_m = functions.convert_ft_to_m(aircraft_altitude_ft)

    aircraft_position = functions.calculate_new_position(traffic_approach.final_approach_fix[0],
                                                         traffic_approach.final_approach_fix[1],
                                                         traffic_approach.heading,
                                                         traffic_approach.final_approach_segment_nm - ref_distance_nm,
                                                         aircraft_altitude_m
                                                        )
    return aircraft_position

def determine_approach_case(distance):
    # which approach scenario is this?
    start_trigger = traffic_approach.start_separation_minima_segment_nm
    stop_trigger = traffic_approach.threshold_segment_nm

    case = 'case4'  # Default case - no traffic
    if distance < stop_trigger: case = 'case3'
    elif stop_trigger <= distance <= start_trigger: case = 'case2'
    elif distance > start_trigger: case = 'case1'

    return case

def create_case_folder(path, name):
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Folder '{name}' created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # define some situational variables here    
    active_runway = '26L'
    traffic_category = aircraft_categories.CAT_D() # set cat a flight
    #traffic_distance_from_threshold_nm = 10 # nm
    

    # determine traffic and evtol approach classes to retrieve attributes
    traffic_approach_class = determine_traffic_approach_class(active_runway)
    traffic_approach = traffic_approach_class()

    evtol_approach_class = determine_evtol_approach_class(traffic_approach)
    evtol_approach = evtol_approach_class()
    
    # create a working folder for current approach
    folder_name = evtol_approach.name +traffic_category.name
    parent_folder = 'Results/' + folder_name
    create_case_folder(parent_folder, folder_name)

    # approach cases instantiated
    case1 = approach.ApproachCase(random.uniform(traffic_approach.start_separation_minima_segment_nm, traffic_approach.final_approach_segment_nm)) # traffic between faf and start
    case2a = approach.ApproachCase(traffic_approach.start_separation_minima_segment_nm) # traffic at start of separation
    case2b = approach.ApproachCase(random.uniform(traffic_approach.end_separation_minima_segment_nm, traffic_approach.final_approach_segment_nm - traffic_approach.start_separation_minima_segment_nm)) # traffic in the middle of separation
    case2c = approach.ApproachCase(traffic_approach.end_separation_minima_segment_nm) # traffic at end of separation
    case3 = approach.ApproachCase(random.uniform(0, traffic_approach.end_separation_minima_segment_nm)) # traffic between end of separation and threshold
    case4 = approach.ApproachCase(0) # no aircraft on approach
    
    cases = {
    'Case_1': case1, 
    'Case_2a': case2a, 
    'Case_2b': case2b, 
    'Case_2c': case2c, 
    'Case_3': case3, 
    'Case_4': case4
    }
    
    
    for case_name, approach_case in cases.items():
        # define a case folder name for all trajectories drawn
        foldername = case_name
        casefolder = parent_folder + '/' + foldername
        create_case_folder(casefolder, foldername)
        
        # determine aircraft position in (lat, long, alt[m])
        aircraft_position = determine_aircraft_position(approach_case.distance)
        
        # construct restricted area
        #trajectoryDesign.construct_restricted_areas(casefolder, aircraft_position, traffic_approach, evtol_approach, traffic_category)
        if approach_case == case1 or approach_case == case4 or approach_case == case3:
            # direct approach
            trajectory_design.construct_restricted_areas(casefolder, aircraft_position, traffic_approach, evtol_approach, traffic_category)
            trajectory_design.construct_direct_approach(casefolder, evtol_approach)

        else:
            # detour_approach
            trajectory_design.construct_restricted_areas(casefolder, aircraft_position, traffic_approach, evtol_approach, traffic_category)
            trajectory_design.construct_detour_approach(casefolder, aircraft_position, traffic_approach, evtol_approach, traffic_category)
