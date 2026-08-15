import functions
from parameters import Traffic, eVTOL

# approach case to be used in throughput
class ApproachCase:
    def __init__(self, distance):
        self.distance = distance


# Base Class for the Approaches at EDDM
class Approach:
    def __init__(self, runway, coordinates, altitude, heading): # each approach is initialized with a reference point and heading
        self.name = self.__class__.__name__
        self.runway = runway # name of runway
        self.coordinates = coordinates  # coordinates for the reference point
        self.altitude = altitude        # altitude/elevation of the reference point in m
        self.heading = functions.adjust_for_restrictedareas(heading) # reference heading for approach definition

    def calculate_final_approach_fix(self, final_approach_segment_nm, altitude_m):
        final_approach_fix = functions.calculate_new_position(
            self.coordinates[0], self.coordinates[1], 
            functions.reciprocal_heading(self.heading), # need reciprocal because we are moving back on the approach
            final_approach_segment_nm, altitude_m
        )
        return final_approach_fix
    
    def calculate_intermediate_fix(self, final_approach_fix, intermediate_approach_segment_nm, altitude_m):
        intermediate_fix = functions.calculate_new_position(
            final_approach_fix[0], final_approach_fix[1], 
            functions.reciprocal_heading(self.heading), 
            intermediate_approach_segment_nm, altitude_m
        )
        return intermediate_fix
    
    def create_kml_output(self, filename, waypoints, labels):
        functions.create_placemarks_kml(filename, waypoints, labels)

# eVTOL Class that inherits from the base class
class eVTOLApproach(Approach):
    def __init__(self, runway, mapt_coordinates, mapt_altitude_ft, 
                 heading, initial_approach_heading, approach_direction):
        
        self.holding_inbound = functions.adjust_for_restrictedareas(self.holding_inbound) # adjust heading
        
        mapt_altitude_m = functions.convert_ft_to_m(mapt_altitude_ft)
        mapt_coordinates = mapt_coordinates + (mapt_altitude_m,)
        
        super().__init__(runway, mapt_coordinates, mapt_altitude_m, heading)

        self.initial_approach_heading = initial_approach_heading
        self.approach_direction = approach_direction
        
        self.calculate_fixes()

        self.get_approach_waypoints()
    
    def calculate_fixes(self):
        self.final_approach_fix = self.calculate_final_approach_fix(
            functions.convert_m_to_nm(eVTOL.final_approach_segment_m), 
            functions.convert_ft_to_m(eVTOL.cruise_altitude_ft) # FAF altitude is the eVTOL cruise altitude  
        )

        self.intermediate_fix = self.calculate_intermediate_fix(
            self.final_approach_fix,
            eVTOL.intermediate_approach_segment_nm, 
            functions.convert_ft_to_m(eVTOL.cruise_altitude_ft) # IF altitude is the eVTOL cruise altitude  
        )

        self.initial_approach_fix = functions.calculate_new_position(
            self.intermediate_fix[0], self.intermediate_fix[1], 
            functions.reciprocal_heading(self.initial_approach_heading) , 
            eVTOL.initial_approach_segment_nm, 
            functions.convert_ft_to_m(eVTOL.cruise_altitude_ft) # IAF altitude is the eVTOL cruise altitude  
        )

        self.holding_fix = self.initial_approach_fix

    def get_approach_waypoints(self):
        self.approach_waypoints = {
            'IAF_'+ self.runway: self.initial_approach_fix,
            'IF_' + self.runway: self.intermediate_fix,
            'FAF_'+ self.runway: self.final_approach_fix,
            'MAPT_' + self.runway: self.coordinates
        } # create dictionary of waypoints

        self.labels = list(self.approach_waypoints.keys())
        self.waypoints = list(self.approach_waypoints.values())

        #self.filename = 'Output_Map_Files/wapoints'+ self.runway + self.approach_direction + '.kml'
        #self.create_kml_output(self.filename, self.waypoints, self.labels)

#create classes for the eVTOL approach directions at EDDM: 26C and 08C
#the reference point for eVTOL Approaches is the Missed Approach Point (MAPt)
#the values here are extracted from the work by Reinisch

class Approach08C(eVTOLApproach):
    def __init__(self, heading, initial_approach_heading, approach_direction):
        
        runway = '08C'
        mapt_coordinates = (48.347896865765669, 11.709873730758749) # mapt coordinates 
        mapt_altitude_ft = 1986 # mapt altitude
        #heading = 81 
        
        super().__init__(runway, mapt_coordinates, 
                         mapt_altitude_ft, heading, 
                        initial_approach_heading,
                        approach_direction)
        
class Approach26C(eVTOLApproach):
    def __init__(self, heading, initial_approach_heading, approach_direction):
        
        runway = '26C'
        mapt_coordinates = (48.353590368844003, 11.783545463078482) # mapt coordinates 
        mapt_altitude_ft = 1986 # mapt altitude
        #heading = 261 
        
        super().__init__(runway, mapt_coordinates, 
                         mapt_altitude_ft, heading, 
                         initial_approach_heading,
                         approach_direction)

class Approach26CNorth(Approach26C):
    def __init__(self):
        heading = 261       
        self.initial_approach_heading = functions.compute_heading(heading,
                                                                  90,
                                                                  'subtract') # heading of initial segment
        self.intermediate_turn = 'right'
        self.holding_inbound = heading
        self.approach_direction = 'North'
        
        super().__init__(heading, self.initial_approach_heading, self.approach_direction)
        
class Approach26CSouth(Approach26C):
    def __init__(self):       
        heading = 261
        self.initial_approach_heading = functions.compute_heading(heading,
                                                                  90,
                                                                  'add') # heading of initial segment
        self.intermediate_turn = 'left'
        self.holding_inbound = functions.reciprocal_heading(heading)
        self.approach_direction = 'South'
        
        super().__init__(heading, self.initial_approach_heading, self.approach_direction)

class Approach08CNorth(Approach08C):
    def __init__(self):       
        heading = 81
        self.initial_approach_heading = functions.compute_heading(heading,
                                                                  90,
                                                                  'add')# heading of initial segment
        self.intermediate_turn = 'left'
        self.holding_inbound = functions.reciprocal_heading(heading)
        self.approach_direction = 'North'
        
        super().__init__(heading, self.initial_approach_heading, self.approach_direction)

class Approach08CSouth(Approach08C):
    def __init__(self):       
        heading = 81
        self.initial_approach_heading = functions.compute_heading(heading, 
                                                                  90, 'subtract'    
        ) # heading of initial segment
        self.intermediate_turn = 'right'
        self.holding_inbound = heading
        self.approach_direction = 'South'
        
        super().__init__(heading, self.initial_approach_heading, self.approach_direction)

# ----- [Traffic Approach class]  ------- #
        
class TrafficApproach(Approach):
    def __init__(self, runway, runway_coordinates, runway_elevation_ft, heading):
        self.runway_elevation_ft = runway_elevation_ft
        runway_elevation_m = functions.convert_ft_to_m(runway_elevation_ft)
        runway_coordinates = runway_coordinates + (runway_elevation_m,)
        
        super().__init__(runway, runway_coordinates, runway_elevation_m, heading)
        
        self.recalculate_approach_segments() # correct assumed faf with accurate rwy elevation

        self.calculate_fixes()

        self.get_approach_waypoints()
    
    def recalculate_approach_segments(self):
        self.final_approach_segment_nm = functions.calculate_segment_glideslope_nm(self.runway_elevation_ft,
                                                                                   Traffic.final_approach_fix_altitude_ft,
                                                                                   Traffic.glideslope_angle_deg)
        
        # distance of start point from runway threshold
        self.start_separation_minima_segment_nm = functions.calculate_segment_glideslope_nm(self.runway_elevation_ft,
                                                                                       Traffic.start_separation_minima_altitude_ft, 
                                                                                       Traffic.glideslope_angle_deg)
        
        # distance of end point from runway threshold
        self.end_separation_minima_segment_nm = functions.calculate_segment_glideslope_nm(self.runway_elevation_ft,
                                                                                        Traffic.end_separation_minima_altitude_ft,
                                                                                        Traffic.glideslope_angle_deg)

        self.separation_minima_segment_nm = self.start_separation_minima_segment_nm - self.end_separation_minima_segment_nm  
    def calculate_fixes(self):
        # final approach fix
        self.final_approach_fix = self.calculate_final_approach_fix(
            self.final_approach_segment_nm, 
            functions.convert_ft_to_m(Traffic.final_approach_fix_altitude_ft)
        )

        # get the coordinates of the point
        self.start_separation_minima = functions.calculate_new_position(
            self.final_approach_fix[0], self.final_approach_fix[1], 
            self.heading, 
            self.final_approach_segment_nm - self.start_separation_minima_segment_nm, 
            functions.convert_ft_to_m(Traffic.start_separation_minima_altitude_ft)
        )

        # get the coordinates of the point
        self.end_separation_minima = functions.calculate_new_position(
            self.start_separation_minima[0], self.start_separation_minima[1], 
            self.heading, 
            self.separation_minima_segment_nm,
            functions.convert_ft_to_m(Traffic.end_separation_minima_altitude_ft)
        )

    def get_approach_waypoints(self):
        self.approach_waypoints = {
            'FAF_'+ self.runway: self.final_approach_fix,
            'SPT_' + self.runway: self.start_separation_minima,
            'END_'+ self.runway: self.end_separation_minima,
            'THRSHLD_' + self.runway: self.coordinates
        } # create dictionary of waypoints

        self.labels = list(self.approach_waypoints.keys())
        self.waypoints = list(self.approach_waypoints.values())

        #self.filename = 'Output_Map_Files/wapoints'+ self.runway + '.kml'
        #self.create_kml_output(self.filename, self.waypoints, self.labels)
        
#create classes for the traffic approach directions at EDDM: 26L-08R and 26R-08L.
#the reference point for Traffic Approaches is the runway threshold 
#the values here are extracted from Skyvector [https://skyvector.com/airport/EDDM/Muenchen-Airport]

class Approach26L(TrafficApproach):
    def __init__(self):
        runway = '26L'
        runway_coordinates = (48.3448333, 11.80466667) # threshold coordinates 
        runway_elevation_ft = 1470
        heading = 261 
        super().__init__(runway, runway_coordinates, runway_elevation_ft, heading)

class Approach08R(TrafficApproach):
    def __init__(self):
        runway = '08R'
        runway_coordinates = (48.34066667, 11.751) 
        runway_elevation_ft = 1486
        heading = 81 
        super().__init__(runway, runway_coordinates, runway_elevation_ft, heading)

class Approach26R(TrafficApproach):
    def __init__(self):
        runway = '26R'
        runway_coordinates = (48.36683333, 11.82116667) 
        runway_elevation_ft = 1449
        heading = 261 
        super().__init__(runway, runway_coordinates, runway_elevation_ft, heading)

class Approach08L(TrafficApproach):
    def __init__(self):
        runway = '08L'
        runway_coordinates = (48.36283333, 11.7675) 
        runway_elevation_ft = 1467
        heading = 81 
        super().__init__(runway, runway_coordinates, runway_elevation_ft, heading)


