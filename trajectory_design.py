import math
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import functions
from parameters import Traffic, eVTOL


def create_straight_segment(start_coord, brng, dist_nm, altitude):
    end_coord = functions.calculate_new_position(start_coord[0], start_coord[1], brng, dist_nm, altitude)
    return [(start_coord, end_coord)]

def create_turn_segment(center_coord, start_coord, radius_nm, start_heading, end_heading, turn_direction, altitude):
    
    points = []

    # Determine the step size for the heading based on the direction of the turn
    step = 1 if turn_direction.lower() == 'right' else -1

    # Adjust the end heading for the loop condition based on the turn direction
    if (end_heading <= start_heading):
        end_heading += 360

    if (turn_direction.lower() == 'right' and end_heading <= start_heading) or \
       (turn_direction.lower() == 'left' and end_heading >= start_heading):
        end_heading += step * 360
    
    heading_increments = 5
    arc_length = (heading_increments/360) * math.pi * 2 * radius_nm
    
    # Generate points for the turn
    for heading in range(start_heading, end_heading, step*heading_increments):  # 1-degree increments for smoother turns
        heading = heading % 360
        point = functions.calculate_new_position(start_coord[0], start_coord[1], heading, arc_length, altitude)
        points.append(point)
        start_coord = point
        
    return points

def generate_evtol_trajectories(initial_approach_fix, intermediate_fix, mapt, final_approach_fix, rwy_heading, iaf_heading, turn_direction, altitude):
    coordinates = []

    turn_radius_nm = functions.convert_m_to_nm(eVTOL.RF_turn_radius_m)

    # initial approach segment
    iaf_to_start_of_turn_distance_nm = eVTOL.initial_approach_segment_nm - turn_radius_nm
    start_of_RF_turn = (functions.calculate_new_position(initial_approach_fix[0], initial_approach_fix[1], iaf_heading, iaf_to_start_of_turn_distance_nm, altitude))
    
    coordinates.extend((initial_approach_fix, start_of_RF_turn)) # straight segment

    center_of_turn = functions.calculate_new_position(start_of_RF_turn[0], start_of_RF_turn[1],rwy_heading , turn_radius_nm, altitude)
    coordinates.extend(create_turn_segment(center_of_turn, start_of_RF_turn, turn_radius_nm, iaf_heading, rwy_heading, turn_direction, altitude))

    end_of_RF_turn = coordinates[-1]

    # intermediate approach segment
    coordinates.extend((end_of_RF_turn, final_approach_fix))

    coordinates.append((mapt))

    placemark_coordinates = [initial_approach_fix, intermediate_fix, final_approach_fix, mapt]
    placemark_labels = ['IAF', 'IF', 'FAF', 'MAPt']

    return coordinates, placemark_coordinates, placemark_labels

def generate_evtol_detour_trajectories(detour_heading, detour_fix, detour_intermediate_fix, initial_approach_fix, mapt, final_approach_fix, rwy_heading, iaf_heading, turn_direction, altitude):
    coordinates = []

    turn_radius_nm = functions.convert_m_to_nm(eVTOL.RF_turn_radius_m)
    

    detour_segment_nm = functions.distance_between_two_points(initial_approach_fix[0],
                                                           initial_approach_fix[1],
                                                           detour_fix[0],
                                                           detour_fix[1])
    # detour segment - IAF to detour fix
    iaf_to_detour_turn_distance_nm = detour_segment_nm - turn_radius_nm
    start_of_detour_turn = (functions.calculate_new_position(initial_approach_fix[0], 
                                                             initial_approach_fix[1], 
                                                             detour_heading, 
                                                             iaf_to_detour_turn_distance_nm, 
                                                             altitude))
    
    coordinates.extend((initial_approach_fix, start_of_detour_turn)) # straight segment - 1

    center_of_detour_turn = functions.calculate_new_position(start_of_detour_turn[0], 
                                                      start_of_detour_turn[1],
                                                      iaf_heading, 
                                                      turn_radius_nm, 
                                                      altitude)
    
    #2nd segment
    coordinates.extend(create_turn_segment(center_of_detour_turn, 
                                           start_of_detour_turn, 
                                           turn_radius_nm, 
                                           detour_heading, 
                                           iaf_heading, 
                                           turn_direction, 
                                           altitude))

    end_of_detour_turn = coordinates[-1]
    
    # detour approach segment
    detour_to_start_of_IF_turn_distance_nm = eVTOL.initial_approach_segment_nm - 2*turn_radius_nm
    start_of_IF_turn = (functions.calculate_new_position(end_of_detour_turn[0], 
                                                         end_of_detour_turn[1], 
                                                         iaf_heading, 
                                                         detour_to_start_of_IF_turn_distance_nm, 
                                                         altitude))
    # 3rd segment
    coordinates.extend((end_of_detour_turn, start_of_IF_turn)) # straight segment

    center_of_IF_turn = functions.calculate_new_position(start_of_IF_turn[0], 
                                                         start_of_IF_turn[1],
                                                         rwy_heading, 
                                                         turn_radius_nm, 
                                                         altitude)
    # 4th segment
    coordinates.extend(create_turn_segment(center_of_IF_turn, 
                                           start_of_IF_turn, 
                                           turn_radius_nm, 
                                           iaf_heading, 
                                           rwy_heading, 
                                           turn_direction, 
                                           altitude))

    end_of_IF_turn = coordinates[-1]

    # 5th segment
    coordinates.extend((end_of_IF_turn, final_approach_fix))

    coordinates.append((mapt))

    placemark_coordinates = [initial_approach_fix, detour_fix, detour_intermediate_fix, final_approach_fix, mapt]
    placemark_labels = ['IAF','DF', 'DIF', 'FAF', 'MAPt']

    return coordinates, placemark_coordinates, placemark_labels

def generate_traffic_trajectories(approach):

    coordinates = approach.waypoints 
    placemark_coordinates = approach.waypoints
    placemark_labels = approach.labels

    return coordinates, placemark_coordinates, placemark_labels

def generate_restricted_areas_corner_points(aircraft_position, evtol_approach, traffic_approach, category):
    coordinates = []
    #waypoints = traffic_approach.waypoints # waypoint order is FAF, SPT, END, THRESHOLD
    traffic_position = aircraft_position

    # corner1
    ntz_aircraft = functions.calculate_new_position(
            traffic_position[0], traffic_position[1], 
            evtol_approach.initial_approach_heading,
            functions.convert_m_to_nm(Traffic.ntz_distance_m), 
            traffic_position[2]
        )
    
    coordinates.append(ntz_aircraft)

    # corner2
    radarsep_aircraft = functions.calculate_new_position(
            traffic_position[0], traffic_position[1], 
            functions.reciprocal_heading(evtol_approach.initial_approach_heading),
            Traffic.radar_separation_nm, 
            traffic_position[2]
        )
    coordinates.append(radarsep_aircraft)

    # corner3
    radarsep_wake_turbulence_distance = functions.calculate_new_position(
            radarsep_aircraft[0], radarsep_aircraft[1], 
            functions.reciprocal_heading(traffic_approach.heading),
            category.separation, 
            traffic_position[2]
        )
    coordinates.append(radarsep_wake_turbulence_distance)

    # corner3
    ntz_wake_turbulence_distance = functions.calculate_new_position(
            ntz_aircraft[0], ntz_aircraft[1], 
            functions.reciprocal_heading(traffic_approach.heading),
            category.separation, 
            traffic_position[2]
        )
    
    coordinates.append(ntz_wake_turbulence_distance)

    return coordinates

def generate_holding_pattern(holding_fix, 
                             inbound_heading, leg_length_nm, turn_radius_nm, altitude):
    coordinates = []
    
    # Calculate opposite direction of inbound heading
    outbound_heading = (inbound_heading + 180) % 360
    
    # Create outbound turn
    turn_center_outbound =functions.calculate_new_position(holding_fix[0], holding_fix[1], inbound_heading + 90, turn_radius_nm, altitude)
    coordinates.extend(create_turn_segment(turn_center_outbound, holding_fix, turn_radius_nm, inbound_heading, outbound_heading, 'right', altitude))
    abeam_fix = coordinates[-1]
    
    # Create outbound leg
    outbound_end = functions.calculate_new_position(abeam_fix[0], abeam_fix[1], outbound_heading, leg_length_nm, altitude)
    coordinates.extend((abeam_fix, outbound_end))
    
    # Create inbound turn
    turn_center_inbound = functions.calculate_new_position(outbound_end[0], outbound_end[1], outbound_heading + 90, turn_radius_nm, altitude)
    coordinates.extend(create_turn_segment(turn_center_inbound, outbound_end, turn_radius_nm, outbound_heading, inbound_heading, 'right', altitude))
    inbound_start =coordinates[-1]

    # Create inbound leg
    coordinates.extend((inbound_start, holding_fix))
    
    
    # Close the pattern by connecting back to the start
    coordinates.append(coordinates[0])

    return coordinates    

def construct_all_trajectories():
    # create evtol trajectories and holdings
    evtol_approaches = [approach.Approach26CSouth(),
                        approach.Approach26CNorth(),
                        approach.Approach08CSouth(),
                        approach.Approach08CNorth()
                    ]

    for approach in evtol_approaches:
        holding_coordinates = generate_holding_pattern(approach.holding_fix, 
                                            approach.holding_inbound, 
                                            functions.convert_m_to_nm(eVTOL.holding_straight_segment_m), 
                                            functions.convert_m_to_nm(eVTOL.holding_turn_radius_m), 
                                            functions.convert_ft_to_m(eVTOL.holding_altitude_ft)
        )
        filepath = "Output_Map_Files/holding_" +approach.runway + approach.approach_direction + ".kml"
        functions.create_path_kml(filepath, holding_coordinates)

        evtol_approach_coordinates = generate_evtol_trajectories(approach.initial_approach_fix, 
                                                    approach.coordinates, 
                                                    approach.final_approach_fix, 
                                                    approach.heading, 
                                                    approach.initial_approach_heading, 
                                                    approach.intermediate_turn, 
                                                    functions.convert_ft_to_m(eVTOL.cruise_altitude_ft)
        )
        filepath = "Output_Map_Files/evtol_approach_" +approach.runway + approach.approach_direction + ".kml"
        functions.create_path_kml(filepath, evtol_approach_coordinates)


    # create approach trajectory
    traffic_approaches = [approach.Approach26L(),
                        approach.Approach26R(),
                        approach.Approach08L(),
                        approach.Approach08R()]

    for approach in traffic_approaches:
        traffic_approach_coordinates = generate_traffic_trajectories(approach)
        filepath = "Output_Map_Files/traffic_approach_" + approach.runway + ".kml"
        functions.create_path_kml(filepath, traffic_approach_coordinates)

def construct_restricted_areas(casefolder, aircraft_position, traffic_approach, evtol_approach, traffic_category):
    # placemarker for a/c position
    filepath = casefolder + '/aircraft_position.kml'
    functions.create_placemarks_kml(filepath,
                                    [aircraft_position],
                                    ['ac'])
    # aircraft trajectories
    traffic_approach_coordinates, waypoints, labels = generate_traffic_trajectories(traffic_approach)
    filepath = casefolder + "/traffic_approach_" + traffic_approach.runway + ".kml"
    functions.create_path_kml(filepath, traffic_approach_coordinates)

    # placemarkers for waypoints 
    filepath = casefolder + '/waypoints_traffic.kml'
    functions.create_placemarks_kml(filepath,waypoints, labels)

    # create a placemark for aircraft position as well
    corners = generate_restricted_areas_corner_points(aircraft_position,
                                                      evtol_approach, 
                                                      traffic_approach, 
                                                      traffic_category)
    
    filepath = casefolder + "/restricted_area" + traffic_approach.runway + traffic_category.name + ".kml"
    functions.create_restricted_area_kml(filepath, corners)

def construct_direct_approach(casefolder, evtol_approach):
    
    # holdings
    holding_coordinates = generate_holding_pattern(evtol_approach.holding_fix, 
                                            evtol_approach.holding_inbound, 
                                            functions.convert_m_to_nm(eVTOL.holding_straight_segment_m), 
                                            functions.convert_m_to_nm(eVTOL.holding_turn_radius_m), 
                                            functions.convert_ft_to_m(eVTOL.holding_altitude_ft)
        )
    filepath = casefolder + "/holding_" +evtol_approach.runway + evtol_approach.approach_direction + ".kml"
    functions.create_path_kml(filepath, holding_coordinates)

    # evtol_approach
    evtol_approach_coordinates, waypoints, labels = generate_evtol_trajectories(evtol_approach.initial_approach_fix,
                                                evtol_approach.intermediate_fix, 
                                                evtol_approach.coordinates, 
                                                evtol_approach.final_approach_fix, 
                                                evtol_approach.heading, 
                                                evtol_approach.initial_approach_heading, 
                                                evtol_approach.intermediate_turn, 
                                                functions.convert_ft_to_m(eVTOL.cruise_altitude_ft)
    )
    
    filepath = casefolder + "/evtol_approach_" +evtol_approach.runway + evtol_approach.approach_direction + ".kml"
    functions.create_path_kml(filepath, evtol_approach_coordinates)

    # placemarkers for waypoints 
    filepath = casefolder + '/waypoints.kml'
    functions.create_placemarks_kml(filepath,waypoints, labels)

def construct_detour_approach(casefolder, aircraft_position, traffic_approach, evtol_approach, traffic_category):
    # get coordinates of restricted areas
    corners = generate_restricted_areas_corner_points(aircraft_position,
                                                      evtol_approach, 
                                                      traffic_approach, 
                                                      traffic_category)
    end_ntz = corners[-1] 
    
    detour_turn_allowance_nm = 0.1 # allowance for detout turn
    # calculate the detour fix and reposistion intermediate fix
    detour_adjacent_ntz = functions.calculate_new_position(
        end_ntz[0], end_ntz[1], 
        evtol_approach.initial_approach_heading,
        functions.convert_m_to_nm(Traffic.noz_distance_m), 
        functions.convert_ft_to_m(eVTOL.cruise_altitude_ft) #IF altitude
    )

    detour_intermediate_fix = functions.calculate_new_position(
        detour_adjacent_ntz[0], detour_adjacent_ntz[1], 
        functions.reciprocal_heading(evtol_approach.heading),
        detour_turn_allowance_nm, 
        functions.convert_ft_to_m(eVTOL.cruise_altitude_ft) #IF altitude
    )
    detour_fix = functions.calculate_new_position(
        detour_intermediate_fix[0], detour_intermediate_fix[1], 
        functions.reciprocal_heading(evtol_approach.initial_approach_heading),
        eVTOL.initial_approach_segment_nm, 
        functions.convert_ft_to_m(eVTOL.cruise_altitude_ft) #IF altitude
    )

    detour_heading = functions.reciprocal_heading(evtol_approach.heading)
    # holdings
    holding_coordinates = generate_holding_pattern(evtol_approach.holding_fix, 
                                            evtol_approach.holding_inbound, 
                                            functions.convert_m_to_nm(eVTOL.holding_straight_segment_m), 
                                            functions.convert_m_to_nm(eVTOL.holding_turn_radius_m), 
                                            functions.convert_ft_to_m(eVTOL.holding_altitude_ft)
        )
    filepath = casefolder + "/holding_" +evtol_approach.runway + evtol_approach.approach_direction + ".kml"
    functions.create_path_kml(filepath, holding_coordinates)

    # approach
    evtol_detour_approach_coordinates, waypoints,labels = generate_evtol_detour_trajectories(detour_heading,
                                                detour_fix,
                                                detour_intermediate_fix,
                                                evtol_approach.initial_approach_fix, 
                                                evtol_approach.coordinates, 
                                                evtol_approach.final_approach_fix, 
                                                evtol_approach.heading, 
                                                evtol_approach.initial_approach_heading, 
                                                evtol_approach.intermediate_turn, 
                                                functions.convert_ft_to_m(eVTOL.cruise_altitude_ft)
    )
    
    filepath = casefolder + "/evtol__detour_approach_" +evtol_approach.runway + evtol_approach.approach_direction + ".kml"
    functions.create_path_kml(filepath, evtol_detour_approach_coordinates)

    # placemarkers for waypoints 
    filepath = casefolder + '/waypoints_detour.kml'
    functions.create_placemarks_kml(filepath,waypoints, labels)