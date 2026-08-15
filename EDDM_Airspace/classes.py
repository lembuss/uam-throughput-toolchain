#####
# Class definitions

#####
import copy

import globals
import numpy as npy
import helperFunctions as util
import matplotlib.pyplot as plt
import matplotlib.colors as mplcolors
from matplotlib import gridspec as gs
from matplotlib import ticker
import json
import dask

# class for all waypoints, parent class for runway thresholds
class Waypoint:
    def __init__(self, name, degNS, degEW, **kwargs):
        self.name = name
        self.coord_x, self.coord_y = self._calcXY4gpsDec(degNS, degEW)

    # calculate xy-coordinates from GPS decimal coordinates
    def _calcXY4gpsDec(self, degNS, degEW):
        lat, lon = util.coordDeg2LatLon(degNS), util.coordDeg2LatLon(degEW)
        x, y = util.coordLatLon2XY(globals.referenceCoordLatLon[0], globals.referenceCoordLatLon[1], lat, lon)
        return x, y

# class for runway thresholds
class Threshold(Waypoint):
    instances = []
    def __init__(self, altitude, **kwargs):
        super().__init__(**kwargs)
        self.altitude = altitude
        self.orientation = []
        Threshold.instances.append(self)

    @classmethod
    def calcOrientations(cls):
        def getOppositeThreshold():
            hdg = int(threshold.name.split()[1][0:2])
            letter = threshold.name[-1]
            name = 'RWY ' + str((hdg + 18) % 36)
            if letter == 'R':
                name = name + 'L'
            elif letter == 'L':
                name = name + 'R'
            elif letter == 'C':
                name = name + 'C'
            return [instance for instance in cls.instances if instance.name == name]

        for threshold in cls.instances:
            if len(threshold.orientation) < 1:
                opposite = getOppositeThreshold()
                delta_x, delta_y = threshold.coord_x - opposite[0].coord_x, threshold.coord_y - opposite[0].coord_y
                threshold.orientation = [delta_x, delta_y]
                opposite[0].orientation = [-delta_x, -delta_y]

# parent class for departure and arrivals routes
class AircraftRoute:
    instances = [] # list of all routes
    def __init__(self, name, waypoints, gradient, remarks, name_type, **kwargs):
        self.name = name
        self.name_type = name_type
        self.waypoints = waypoints
        self.gradient = gradient
        self.remarks = remarks
        self.plotted = True
        self.coord_x = []
        self.coord_y = []
        self.altitudes = []
        self.height_below = [] # includes vertical separation
        AircraftRoute.instances.append(self)

        self._calcXY4Route() # calculate xy-coordinates from route waypoints' gps-coordinates

    # return routes sorted by type (SID, approach)
    @classmethod
    def getRoutesSorted(cls):
        result = {}
        for instance in cls.instances:
            if instance.name_type in result:
                result[instance.name_type].append([instance.name, instance])
            else:
                result[instance.name_type] = [[instance.name, instance]]
        return result

    @classmethod
    def plotRoutes(cls, axis):
        colors = mplcolors.TABLEAU_COLORS
        color_keys = list(colors)
        color_index = -1
        current_name_type = ''

        geojson = {
        "type": "FeatureCollection",
        "features": []
        }

        for instance in cls.instances:
            if current_name_type != instance.name_type:
                color_index += 1
                current_name_type = instance.name_type
            if instance.plotted:
                # switch colors based on departure runway
                axis.plot(instance.coord_x, instance.coord_y, instance.altitudes, color=colors[color_keys[color_index]],
                          label=instance.name)
            
            # create GeoJson objects for Airbus Russ-Tool for the contour data
            
             
            formatted_list = []
            for x, y, z in zip(instance.coord_x, instance.coord_y, instance.altitudes):
                formatted_list.append((x, y, z))

            path = util.coordXY2LatLon2(globals.referenceCoordLatLon, formatted_list)
        

            feature = {
                "type": "Feature",
            
                "geometry": {
                    "type": "LineString",
                    "coordinates": path
                }
            }
            geojson["features"].append(feature)
            
       

        # write the GeoJSON data to a file

        features_str = []
        for feature in geojson["features"]:
            feature_str = json.dumps(feature, indent=4)
            features_str.append(feature_str)

        
        with open("plotqgisroutes.geojson", "w") as f:
            f.write("{\n")
            f.write(f'"type": "FeatureCollection",\n')
            f.write(f'"features": [\n')
            f.write(",\n".join(features_str))
            f.write("\n]\n")
            f.write("}")

    @classmethod
    def plotContour(cls, axis):
        grid_x, grid_y, contour_data = globals.getXYGridAndZValues()
        for instance in cls.instances:
            if instance.plotted and not instance.name == ("APCH 08C") and not instance.name==("APCH 26C") and not instance.name==("GUDEG 8C") and not instance.name==("MAGAT 2C"):
                # calculate contour plot based on plotted routes
                contour_data = npy.fmin(contour_data, instance.height_below)
        contour = axis.contour(grid_x, grid_y, contour_data + globals.refTerrain, levels=40)  #<--- levels changed from 40


        
        # create GeoJson objects for Airbus Russ-Tool for the contour data
        
        geojson = {
        "type": "FeatureCollection",
        "features": []
        }
        
        for level, collection in zip(contour.levels, contour.collections):

            for path in collection._segments3d:
                 

                path = util.coordXY2LatLon(globals.referenceCoordLatLon, path)
                
                feature = {
                    "type": "Feature",
                    
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": path
                     },
                    "properties": {
                        "value": level
                    }
                }
                geojson["features"].append(feature)
                
       

        # write the GeoJSON data to a file

        features_str = []
        for feature in geojson["features"]:
            feature_str = json.dumps(feature, indent=4)
            features_str.append(feature_str)

        
        with open("plotairbus.geojson", "w") as f:
            f.write("{\n")
            f.write(f'"type": "FeatureCollection",\n')
            f.write(f'"features": [\n')
            f.write(",\n".join(features_str))
            f.write("\n]\n")
            f.write("}")

     # create GeoJson objects for QGis for the contour data
        
        geojson = {
        "type": "FeatureCollection",
        "features": []
        }
        id = 0
        for level, collection in zip(contour.levels, contour.collections):

            for path in collection._segments3d:
                 

                path = util.coordXY2LatLon(globals.referenceCoordLatLon, path)
                
                feature = {
                    "type": "Feature",
                    "id": id,
                    "geometry": {
                        "type": "LineString",
                        "coordinates": path
                     },
                    "properties": {
                        "value": util.convft2m(level)
                    }
                }
                geojson["features"].append(feature)
                id += 1
       

        # write the GeoJSON data to a file

        features_str = []
        for feature in geojson["features"]:
            feature_str = json.dumps(feature, indent=4)
            features_str.append(feature_str)

        
        with open("plotqgis.geojson", "w") as f:
            f.write("{\n")
            f.write(f'"type": "FeatureCollection",\n')
            f.write(f'"features": [\n')
            f.write(",\n".join(features_str))
            f.write("\n]\n")
            f.write("}")

    # get xy-coordinates for waypoints of route from waypoint list
    def _calcXY4Route(self):
        waypointList = globals.getWaypointList()

        for waypoint in self.waypoints:
            if waypoint[0:3] == 'DME': # special treatment for waypoints that are defined as distance from a DME (departures only)
                distance = float(waypoint[8:11].replace(',', '.'))
                x_dme, y_dme = waypointList[waypoint[0:7]].coord_x, waypointList[waypoint[0:7]].coord_y
                rwy_orientation = waypointList[self.waypoints[0]].orientation
                x, y = util.coordExtendDistFromXY(distance, [x_dme, y_dme], rwy_orientation)
            else:
                x, y = waypointList[waypoint].coord_x, waypointList[waypoint].coord_y
            self.coord_x.append(x)
            self.coord_y.append(y)

    # calculate height between ground and route for points of grid defined in globals.py
    def _calcHeightBelowRoute(self): 
            
        # calculate height below one segment of a route
        def calcHeightBelowSegment():
            # get subgrid around currently calculated route segment
            xy_vectors_sub, height_below_sub, offset_x, offset_y = \
                util.getXYZSubGrids(vec_start, vec_end, globals.getWakeTurbSep(), globals.getXYGridSteps(),
                                    xy_vectors, height_below)
            vec_segment = vec_start - vec_end
            mat_start2point = npy.subtract(xy_vectors_sub, vec_start) # for every point of the grid, get vector to start of segment
            mat_end2point = npy.subtract(xy_vectors_sub, vec_end) # ... and to end of segment
            mat_patch_middle = npy.ones(height_below_sub.shape) # template for points between start and end of segment
                                                                # and within lateral separation (nan-entry for points
                                                                # outside of that range)
            
            # remove points outside of lateral separation
            mat_ortho_length = util.getPoint2VecOthoDist(vec_segment, mat_end2point)
            npy.place(mat_patch_middle, mat_ortho_length > separation_lat, npy.nan)
            height_below_before = mat_patch_middle * util.calcHeight4Altitude(altitude_start) - separation_vert
            height_below_after = mat_patch_middle * util.calcHeight4Altitude(altitude_end) - separation_vert
            
            # remove points before start and after end of segment
            mat_before_start = util.getVec2DAngleNorm(mat_start2point, vec_segment)  # values > 0 are before startpoint of segment
            mat_after_end = util.getVec2DAngleNorm(mat_end2point, vec_segment) # values < 0 are after endpoint of segment
            npy.place(mat_patch_middle, mat_before_start > 0, npy.nan)
            npy.place(mat_patch_middle, mat_after_end < 0, npy.nan)
            
            for threshold in Threshold.instances:
                if threshold.name == "RWY 26L" or threshold.name == "RWY 26R" or threshold.name == "RWY 08L" or threshold.name == "RWY 08R" or threshold.name == "RWY 08C" or threshold.name == "RWY 26C":
                    if npy.all(vec_start == npy.array([threshold.coord_x,threshold.coord_y])):
                        # special treatment for points before start and after end of segment (constant height)
                        mat_dist_start2point = npy.linalg.norm(mat_start2point, axis=2)
                        mat_dist_end2point = npy.linalg.norm(mat_end2point, axis=2)
                        npy.place(height_below_before, mat_dist_start2point > 0, npy.nan)
                        #npy.place(height_below_after, mat_dist_end2point > separation_lat, npy.nan)
            
            # special treatment for points before start and after end of segment (constant height)
            npy.place(height_below_before, mat_before_start <= 0, npy.nan)
            npy.place(height_below_after, mat_after_end >= 0, npy.nan)
            mat_dist_start2point = npy.linalg.norm(mat_start2point, axis=2)
            mat_dist_end2point = npy.linalg.norm(mat_end2point, axis=2)
            npy.place(height_below_before, mat_dist_start2point > separation_lat, npy.nan)
            npy.place(height_below_after, mat_dist_end2point > separation_lat, npy.nan)
            
            # calculate height (only between start and end points)
            altitude_below_middle = -util.getVec2DProjLengthFraction(vec_segment, mat_start2point) * \
                                (altitude_end - altitude_start) + altitude_start - separation_vert # get fraction of segment length for each point and
                                                                                                # multiply with altitude difference
            altitude_below_middle = altitude_below_middle * mat_patch_middle # trim altitude to relevant points
            height_below_middle = util.calcHeight4Altitude(altitude_below_middle)

            # Set Height below segment for final approach section within wake turbolence seperation and lateral seperation from final approach course:

            for threshold in Threshold.instances:
                if npy.all(vec_end == npy.array([threshold.coord_x,threshold.coord_y])): # execute only for Approaches 
                # Remove points within UAV approach corridor and wake turbulence separation of 8 Nm from the conventional final approach segment
                    ParallelApchSep = globals.getParallelApchSep()
    
                # Calculations for approach to RWY 08L
                    if threshold.name == "RWY 08L":
                        mat_ortho_lengthsign = util.getPoint2VecOthoDistsign(vec_segment, mat_end2point) ##
                        mat_start2point = npy.subtract(xy_vectors_sub, vec_start)
                        altitude_below_middle_final08L = -util.getVec2DProjLengthFraction(vec_segment, mat_start2point) * \
                                    (altitude_end - altitude_start) + altitude_start - separation_vert                         # Calcultae height bellow approach path usable for UAV flight 
                        altitude_below_middle = util.slide_elevation_matrix08(altitude_below_middle_final08L , globals.getWakeTurbSep(), globals.getGridSize(), vec_segment) # Slide the usable height bellow the approach path away from the threshold in order to maintain wake turbulence separation
                        mat_patch_middle = npy.ones(height_below_sub.shape)
                        npy.place(mat_patch_middle, mat_ortho_length > separation_lat, npy.nan)
                        altitude_below_middle = altitude_below_middle * mat_patch_middle

                        for indexi, e in enumerate(mat_ortho_lengthsign): # Check if point of grid is between the RWYs 
                            for indexj, f in enumerate(e):
                                if f > 0 and npy.abs(f)>(ParallelApchSep) : # if f > 0 point between the two RWYs
                                    altitude_below_middle[indexi][indexj] = npy.nan # For points between the RWYs and with certain distance to the RWYS set altitude bellow to npy.nan -> approach corridor  

                            height_below_middle = util.calcHeight4Altitude(altitude_below_middle)
                            
                # Calculations for approach to RWY 08R (same procedure as for RWY 08L)
                    if threshold.name == "RWY 08R":
                        mat_ortho_lengthsign = util.getPoint2VecOthoDistsign(vec_segment, mat_end2point)
                        mat_start2point = npy.subtract(xy_vectors_sub, vec_start)
                        altitude_below_middle_final08R = -util.getVec2DProjLengthFraction(vec_segment, mat_start2point) * \
                                    (altitude_end - altitude_start) + altitude_start - separation_vert
                        altitude_below_middle = util.slide_elevation_matrix08(altitude_below_middle_final08R , globals.getWakeTurbSep(), globals.getGridSize(), vec_segment)
                        mat_patch_middle = npy.ones(height_below_sub.shape)
                        npy.place(mat_patch_middle, mat_ortho_length > separation_lat, npy.nan)
                        altitude_below_middle = altitude_below_middle * mat_patch_middle

                        for indexi, e in enumerate(mat_ortho_lengthsign):
                            for indexj, f in enumerate(e):
                                if f < 0 and npy.abs(f)>(ParallelApchSep) :
                                    altitude_below_middle[indexi][indexj] = npy.nan

                            height_below_middle = util.calcHeight4Altitude(altitude_below_middle)
                            
                # Calculations for approach to RWY 26L (same procedure as for RWY 08L)
                    if threshold.name == "RWY 26L":
                        mat_ortho_lengthsign = util.getPoint2VecOthoDistsign(vec_segment, mat_end2point)
                        mat_start2point = npy.subtract(xy_vectors_sub, vec_start)
                        altitude_below_middle_final26L = -util.getVec2DProjLengthFraction(vec_segment, mat_start2point) * \
                                    (altitude_end - altitude_start) + altitude_start - separation_vert
                        altitude_below_middle = util.slide_elevation_matrix26(altitude_below_middle_final26L , globals.getWakeTurbSep(), globals.getGridSize(), vec_segment)
                        mat_patch_middle = npy.ones(height_below_sub.shape)
                        npy.place(mat_patch_middle, mat_ortho_length > separation_lat, npy.nan)
                        altitude_below_middle = altitude_below_middle * mat_patch_middle

                        for indexi, e in enumerate(mat_ortho_lengthsign):
                            for indexj, f in enumerate(e):
                                if f > 0 and npy.abs(f)>(ParallelApchSep) :
                                    altitude_below_middle[indexi][indexj] = npy.nan

                            height_below_middle = util.calcHeight4Altitude(altitude_below_middle)
                            
                # Calculations for approach to RWY 26R (same procedure as for RWY 08L)
                    if threshold.name == "RWY 26R":
                        mat_ortho_lengthsign = util.getPoint2VecOthoDistsign(vec_segment, mat_end2point)
                        mat_start2point = npy.subtract(xy_vectors_sub, vec_start)
                        altitude_below_middle_final26R = -util.getVec2DProjLengthFraction(vec_segment, mat_start2point) * \
                                    (altitude_end - altitude_start) + altitude_start - separation_vert
                        altitude_below_middle = util.slide_elevation_matrix26(altitude_below_middle_final26R , globals.getWakeTurbSep(), globals.getGridSize(), vec_segment)
                        mat_patch_middle = npy.ones(height_below_sub.shape)
                        npy.place(mat_patch_middle, mat_ortho_length > separation_lat, npy.nan)
                        altitude_below_middle = altitude_below_middle * mat_patch_middle

                        for indexi, e in enumerate(mat_ortho_lengthsign):
                            for indexj, f in enumerate(e):
                                if f < 0 and npy.abs(f)>(ParallelApchSep) :
                                    altitude_below_middle[indexi][indexj] = npy.nan

                            height_below_middle = util.calcHeight4Altitude(altitude_below_middle)
                            
            # get lowest height of: existing entries (_sub), calculated for segment between start and end (_middle),
            # calculated for before start of segment (_before) and calculated for after end of segment (_after)
            height_below_sub = npy.fmin(
                npy.fmin(
                    npy.fmin(height_below_sub, height_below_middle),
                    height_below_before),
                height_below_after)
            
            if globals.debug:
                debug_plot2DRouteSegmentWithGrid([vec_start[0], vec_end[0]], [vec_start[1], vec_end[1]], globals.getXYGridSteps(), height_below_sub, offset_x, offset_y)
            
            # override grid with subgrid
            height_below[offset_y:len(height_below_sub) + offset_y, offset_x:len(height_below_sub[0]) + offset_x] = \
                height_below_sub

            """
            #Departure corridors:

            xystart08 = util.coordLatLon2XY(globals.referenceCoordLatLon[0], globals.referenceCoordLatLon[1], 48.350796588487277 , 11.747316338032521)

            xyend08 = util.coordLatLon2XY(globals.referenceCoordLatLon[0], globals.referenceCoordLatLon[1], 48.38878013451729 , 12.25370231707349)

            xystart26 = util.coordLatLon2XY(globals.referenceCoordLatLon[0], globals.referenceCoordLatLon[1], 48.350702534771571 , 11.746099319349849)

            xyend26 = util.coordLatLon2XY(globals.referenceCoordLatLon[0], globals.referenceCoordLatLon[1], 48.312661980795696, 11.26721594184963)


            print(xystart08,xyend08,xystart26,xyend26)

            # <--- Find Start and end Point of UAV departure corridors. For the moment manually saved to globals
            #     vec_start26C = vec_start
            # if self.name==("MAGAT 2C"): 
            #     vec_start26C = vec_start
            #     vec_end26C = npy.array([globals.getWaypointList()[self.waypoints[-1]].coord_x, globals.getWaypointList()[self.waypoints[-1]].coord_y])
            #     print(vec_start26C)
            #     print(vec_end26C)
            # if self.name==("GUDEG 8C"):
            #     vec_start8C = vec_start
            #     vec_end8C = npy.array([globals.getWaypointList()[self.waypoints[-1]].coord_x, globals.getWaypointList()[self.waypoints[-1]].coord_y])
            #     print(vec_start8C)
            #     print(vec_end8C) <---
            
            
            # Setting heights below route to npy.nan within departure cooridor for UAV departures (For the moment manually switching which RWY is in use by commenting out the other RWY):
            #for route in AircraftRoute.instances:
                
            #if self.name==("MAGAT 2C") and self.plotted == True:
            #Set the values within departure corridor 26C to numpy.nan
            # width_UAV_Dep_Corridor = globals.getUAVDepCorridor()  # Width of UAV departure corridor 


            # vec_segment = globals.vec_start26C - globals.vec_end26C
            # mat_start2point = npy.subtract(xy_vectors, globals.vec_start26C) # for every point of the grid, get vector to start of segment
            # mat_end2point = npy.subtract(xy_vectors, globals.vec_end26C) # ... and to end of segment
            # # remove points before start and after end of segment
            # mat_before_start = util.getVec2DAngleNorm(mat_start2point, vec_segment)  # values > 0 are before startpoint of segment
            # mat_ortho_length = util.getPoint2VecOthoDist(vec_segment, mat_end2point)
            # conditionDep = npy.logical_and(mat_before_start < 0, mat_ortho_length < width_UAV_Dep_Corridor/2)
            # npy.place(height_below, conditionDep , npy.nan)

                                                                        
                

            # if self.name==("GUDEG 8C") and self.plotted == True:

            # # Set the values within departure corridor 8C to numpy.nan
            width_UAV_Dep_Corridor = globals.getUAVDepCorridor()  # Width of UAV departure corridor 


            vec_segment = globals.vec_start8C - globals.vec_end8C
            mat_start2point = npy.subtract(xy_vectors, globals.vec_start8C) # for every point of the grid, get vector to start of segment
            mat_end2point = npy.subtract(xy_vectors, globals.vec_end8C) # ... and to end of segment


            # remove points before start and after end of segment
            mat_before_start = util.getVec2DAngleNorm(mat_start2point, vec_segment)  # values > 0 are before startpoint of segment
            mat_ortho_length = util.getPoint2VecOthoDist(vec_segment, mat_end2point)
            condition = npy.logical_and(mat_before_start < 0, mat_ortho_length < width_UAV_Dep_Corridor/2)

            npy.place(height_below, condition , npy.nan)

            # Extension of approach corridors for RWY 26 from threshold 26R to Threshold of UAV RWY:
                #This is not necessary for RWY 08 because UAV approach corridor reaches UAV departure corridor because the threshold RYW 08 UAV
                # is located further west than the threshold 08R of the conventional traffic  


            # width_UAV_App_Corridor = 540  # Width of UAV approach corridor 


            # vec_segment = globals.vec_start26C - globals.vec_end26C
            # mat_start2point = npy.subtract(xy_vectors, globals.vec_start26C) # for every point of the grid, get vector to start of segment
            # mat_end2point = npy.subtract(xy_vectors, globals.vec_end26C) # ... and to end of segment
            # mat_dist_start2point = npy.linalg.norm(mat_start2point, axis=2)
            # # remove points before start and after end of segment
            # mat_before_start = util.getVec2DAngleNorm(mat_start2point, vec_segment)  # values > 0 are before startpoint of segment
            # mat_ortho_length = util.getPoint2VecOthoDist(vec_segment, mat_end2point)
            # conditionDep = npy.logical_and(mat_before_start > 0, npy.logical_and(mat_dist_start2point< 6000, mat_ortho_length < width_UAV_App_Corridor/2))
            # npy.place(height_below, conditionDep , npy.nan)
            """
        
        xy_vectors, z_matrix = globals.getXYGridVectorsAndZValues() # import xy-grid coordinates and standard z-values
        height_below = copy.deepcopy(z_matrix) # create true copy of standard z-values (otherwise the standard z-values
                                                # will be overwritten because variables in python are pointers by default
                                                # and not separate copies)
        separation_lat = globals.getConvUAMLatSep()
        separation_vert = globals.getConvUAMVSep()
            
        print('Calculating route', self.name)
        for x, y, altitude_end in zip(self.coord_x, self.coord_y, self.altitudes):
            
            if not self.name == ("APCH 08C") or self.name==("APCH 26C") or self.name==("GUDEG 8C") or self.name==("MAGAT 2C"):
                if 'vec_start' in locals(): # skip first iteration
                    vec_end = npy.array([x, y])
                    if util.checkVec2DinXYGrid(vec_start, vec_end, globals.getXYGridSteps()): # only calculate height if segment is within grid
                        calcHeightBelowSegment()
                vec_start = npy.array([x, y])
                altitude_start = altitude_end
                
            height_below = npy.where(height_below < 1000, 0, height_below) # minimum vehicle cruise height 1000 ft, climb and descent in approach and departure corridor 
            
            self.height_below = height_below


# class for departure routes (SIDs)
class InstrumentDeparture(AircraftRoute):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._calcAltitude4Route() # calculate altitude for points of route
        self._calcHeightBelowRoute() # calculate height usable for UAM below the route

    # calculate altitude of aircraft at routes' waypoints
    # calculation is based on the climb gradient defined in the input data, if a maximum altitude is associated with
    # that gradient, the standard gradient will be used thereafter; the maximum altitude is defined in globals.py
    def _calcAltitude4Route(self):

        if self.name ==("GUDEG 8C") or self.name==("MAGAT 2C"):


            def getClimbGradient():
                if self.gradient == 'STD':
                    return globals.stdGradient, globals.maxAltitudeUAV
                else:
                    str_elements = self.gradient.split()
                    return float(str_elements[0].replace(',', '.').replace('%', '')), int(str_elements[2])

            def calcAltitude(vec_start_corr, altitude_start_corr):
                segment_len = util.getVec2DDist(vec_start_corr, vec_end)
                return altitude_start_corr + util.convm2ft(segment_len * gradient / 100)

            waypoints_new = []
            altitudes = [globals.refTerrain]
            gradient, gradient_limit = getClimbGradient()

            # iterate over x-coordinates of waypoints
            for index, x in enumerate(self.coord_x[0:len(self.coord_x) - 1]):
                vec_start = [x, self.coord_y[index]] # vector to waypoint at start of segment
                vec_end = [self.coord_x[index + 1], self.coord_y[index + 1]] # vector to waypoint at end of segment
                altitude_start = altitudes[-1]
                altitude_end = calcAltitude(vec_start, altitude_start) # calculate altitude with current gradient
                if altitude_end > gradient_limit: # aircraft reaches gradient limit before end of segment
                    vec_max = util.getVec2DPosAtValue(vec_start, vec_end, altitude_start, altitude_end, gradient_limit) # get position where gradient limit is reached
                    if gradient_limit != globals.maxAltitudeUAV:  # maximum altitude for climb gradient reached -> change climb gradient to default value
                        waypoints_new.append([index + 1, 'TOG', vec_max])
                        altitudes.append(gradient_limit)
                        gradient, gradient_limit = globals.stdGradient, globals.maxAltitudeUAV
                        altitude_end = calcAltitude(vec_max, altitudes[-1]) # calculate altitude for remaining part of segment with new gradient
                    if altitude_end > globals.maxAltitudeUAV:  # maximum altitude reached
                        waypoints_new.append([index + len(waypoints_new) + 1, 'TOC', vec_max])
                        altitudes_remaining = [globals.maxAltitudeUAV] * (len(self.coord_x) + len(waypoints_new) - len(altitudes))
                        altitudes = altitudes + altitudes_remaining
                        break
                altitudes.append(altitude_end)

            for waypoint_new in waypoints_new: # insert new waypoints
                self.waypoints.insert(waypoint_new[0], waypoint_new[1])
                self.coord_x.insert(waypoint_new[0], waypoint_new[2][0])
                self.coord_y.insert(waypoint_new[0], waypoint_new[2][1])
            self.altitudes = altitudes

        else: 

            def getClimbGradient():
                if self.gradient == 'STD':
                    return globals.stdGradient, globals.maxAltitude
                else:
                    str_elements = self.gradient.split()
                    return float(str_elements[0].replace(',', '.').replace('%', '')), int(str_elements[2])

            def calcAltitude(vec_start_corr, altitude_start_corr):
                segment_len = util.getVec2DDist(vec_start_corr, vec_end)
                return altitude_start_corr + util.convm2ft(segment_len * gradient / 100)

            waypoints_new = []
            altitudes = [globals.refTerrain]
            gradient, gradient_limit = getClimbGradient()

            # iterate over x-coordinates of waypoints
            for index, x in enumerate(self.coord_x[0:len(self.coord_x) - 1]):
                vec_start = [x, self.coord_y[index]] # vector to waypoint at start of segment
                vec_end = [self.coord_x[index + 1], self.coord_y[index + 1]] # vector to waypoint at end of segment
                altitude_start = altitudes[-1]
                altitude_end = calcAltitude(vec_start, altitude_start) # calculate altitude with current gradient
                if altitude_end > gradient_limit: # aircraft reaches gradient limit before end of segment
                    vec_max = util.getVec2DPosAtValue(vec_start, vec_end, altitude_start, altitude_end, gradient_limit) # get position where gradient limit is reached
                    if gradient_limit != globals.maxAltitude:  # maximum altitude for climb gradient reached -> change climb gradient to default value
                        waypoints_new.append([index + 1, 'TOG', vec_max])
                        altitudes.append(gradient_limit)
                        gradient, gradient_limit = globals.stdGradient, globals.maxAltitude
                        altitude_end = calcAltitude(vec_max, altitudes[-1]) # calculate altitude for remaining part of segment with new gradient
                    if altitude_end > globals.maxAltitude:  # maximum altitude reached
                        waypoints_new.append([index + len(waypoints_new) + 1, 'TOC', vec_max])
                        altitudes_remaining = [globals.maxAltitude] * (len(self.coord_x) + len(waypoints_new) - len(altitudes))
                        altitudes = altitudes + altitudes_remaining
                        break
                altitudes.append(altitude_end)

            for waypoint_new in waypoints_new: # insert new waypoints
                self.waypoints.insert(waypoint_new[0], waypoint_new[1])
                self.coord_x.insert(waypoint_new[0], waypoint_new[2][0])
                self.coord_y.insert(waypoint_new[0], waypoint_new[2][1])
            self.altitudes = altitudes

# class for approach routes
class Approach(AircraftRoute):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._calcAltitude4Route() # calculate altitude for points of route
        self._calcHeightBelowRoute() # calculate height usable for UAM below the route

    # calculate altitude of aircraft at routes' waypoints
    # constant altitude for all waypoints, except last one (runway threshold), that one is assigned the correct
    # altitude, drawn from the waypoints list
    def _calcAltitude4Route(self):

            approach_altitude = float(self.remarks[0].split()[1])
            self.altitudes = [approach_altitude] * len(self.waypoints)
            self.altitudes[-1] = globals.getWaypointList()[self.waypoints[-1]].altitude

###
# Debug
###

def debug_plot2DRouteSegmentWithGrid(segmentX, segmentY, gridSteps, gridZ, offset_x, offset_y):
    steps_x = gridSteps[0][offset_x:len(gridZ[0]) + offset_x]
    steps_y = gridSteps[1][offset_y:len(gridZ) + offset_y]
    gridX, gridY = npy.meshgrid(steps_x, steps_y)

    fig = plt.figure("Debug")
    ax = plt.axes()

    ax.plot(segmentX, segmentY, color='black')
    ax.contourf(gridX, gridY, gridZ, levels=40)
    ax.grid(c='k', ls='-', alpha=0.3)
    #ax.plot(gridX, gridY, 'ro')

    ax.xaxis.set_major_locator(ticker.MultipleLocator(globals.grid_size))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(globals.grid_size))

    plt.show()

