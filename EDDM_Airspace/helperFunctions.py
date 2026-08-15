import math
import globals
import numpy as npy
import geopy.distance as geo

norm = npy.linalg.norm

## coordinate transformations ##
# transform from degree coordinates to decimal coordinates
def coordDeg2LatLon(coord_deg):
    directions = {'N': 1, 'S': -1, 'E': 1, 'W': -1}
    deg_elements = coord_deg.split()
    coordDec = float(deg_elements[1]) + float(deg_elements[2]) / 60 + float(deg_elements[3].replace(',', '.')) / 3600
    return coordDec * directions[deg_elements[0]]

# transform from decimal coordinates to xy-coordinates compared to reference
def coordLatLon2XY(lat1, lon1, lat2, lon2):
    y = geo.geodesic((lat1, lon1), (lat2, lon1)).m
    x = geo.geodesic((lat1, lon1), (lat1, lon2)).m
    if lon2 < lon1:
        x = -x
    if lat2 < lat1:
        y = -y
    return x, y

# transform from xy-coordinates compared to reference to decimal coordinates
def coordXY2LatLon(referenceCoordLatLon, xy_coords):

    paths = []

    for path in xy_coords:
        
        xy_coords = list(zip(path[0:1],path[1:2]))
        x = xy_coords[0][0]
        y = xy_coords[0][1]
        referenceCoordLatLon = (referenceCoordLatLon[0],referenceCoordLatLon[1])

        destination = geo.distance(meters=x).destination(point=referenceCoordLatLon, bearing=90)
        destination = geo.distance(meters=y).destination(point=destination, bearing=0)
   
        path = (destination.longitude,destination.latitude)
        paths.append(path)

    return paths


# transform from xy-coordinates compared to reference to decimal coordinates
def coordXY2LatLon2(referenceCoordLatLon, xy_coords):

    paths = []

    for path in xy_coords:
        
        xy_coords = list(zip(path[0:1],path[1:2],path[2:3]))
        x = xy_coords[0][0]
        y = xy_coords[0][1]
        z = xy_coords[0][2]
        referenceCoordLatLon = (referenceCoordLatLon[0],referenceCoordLatLon[1])

        destination = geo.distance(meters=x).destination(point=referenceCoordLatLon, bearing=90)
        destination = geo.distance(meters=y).destination(point=destination, bearing=0)
        z = z * 0.3048 # m in ft
   
        path = (destination.longitude,destination.latitude, z)
        paths.append(path)

    return paths


# extend a certain distance from a xy-coordinate in a given direction (used for DME-waypoints)
# in: distanceNM = distance to extend from reference in NM -> float
#     reference = point to extend from, xy-coordinates -> 2-element array
#     vector = direction in which to extend, xy-coordinates -> 2-element array
# out: coordinates of new point, xy-coordinates -> float, float
def coordExtendDistFromXY(distanceNM: float, reference: [float, float], vector: [float, float]) -> float:
    distance = convNM2m(distanceNM)
    rwyUnitVector = vector / norm(vector)
    x = reference[0] + rwyUnitVector[0] * distance
    y = reference[1] + rwyUnitVector[1] * distance
    return x, y

# calculate height (above ground) from altitude (above sea level)
def calcHeight4Altitude(altitude: float) -> float:
    return altitude - globals.refTerrain

## vector functions ##
# calculate distance between two vectors
def getVec2DDist(vec1, vec2):
    return norm(npy.subtract(vec2, vec1))

# calculate angle between two vectors
def getVec2DAngleNorm(vec1, vec2):
    vec1_norm = vec1 / norm(vec1)
    vec2_norm = vec2 / norm(vec2)
    return vec1_norm.dot(vec2_norm)

# project vector onto another vector and then calculate length fraction of projected vector compared to vector it was projected on
def getVec2DProjLengthFraction(vec, vec_to_project):
    return (vec_to_project.dot(vec)) / (vec.dot(vec))

# project vector onto another vector and then calculate length fraction of projected vector compared to vector it was projected on
def getVec2DProjLength(vec, vec_to_project):
    return (vec_to_project.dot(vec)) 

# get wake turbolence seperation in height bellow matrix for wake turbolence separation in final approach segment:
def slide_elevation_matrix08(matrix, distance, grid_size, vec_segment):
    distance = math.ceil(distance / grid_size)
    slided_matrix = matrix.copy()
    line_direction = vec_segment/npy.linalg.norm(vec_segment)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            z_value = matrix[i][j]

            step_i = int(distance * line_direction[1])
            step_j = int(distance * line_direction[0])


            for ii in range(i, int(i + distance * line_direction[1]), step_i):
                for jj in range(j, int(j + distance * line_direction[0]), step_j):
                    if (0 <= ii < matrix.shape[0]) and (0 <= jj < matrix.shape[1]):
                        slided_matrix[ii][jj] = z_value
    return slided_matrix

# get wake turbolence seperation in height bellow matrix for wake turbolence separation in final approach segment:
def slide_elevation_matrix26(matrix, distance, grid_size, vec_segment):
    distance = math.ceil(distance / grid_size)
    slided_matrix = matrix.copy()
    line_direction = vec_segment/npy.linalg.norm(vec_segment)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):          
            z_value =  matrix[i][j]

            step_i = math.ceil(distance * line_direction[1])+1
            step_j = math.ceil(distance * line_direction[0])+1


            for ii in range(int(i + (distance * line_direction[1])), i,  -step_i):
                for jj in range(int(j + (distance * line_direction[0])), j, -step_j):
                    if (0 <= ii < matrix.shape[0]) and (0 <= jj < matrix.shape[1]):
                        slided_matrix[ii][jj] = z_value
    a = slided_matrix                    
    return slided_matrix

# generating center lines for departure corridor

#def center_line_departures  

# returns the position on an axis defined by vecStart and vecEnd where value = valueSearch
def getVec2DPosAtValue(vecStart, vecEnd, valueStart, valueEnd, valueSearch):
    fraction = (valueSearch - valueStart) / (valueEnd - valueStart)
    return vecStart + npy.subtract(vecEnd, vecStart) * fraction

# checks if vector is in grid
def checkVec2DinXYGrid(vec_start, vec_end, grid_steps):
    x_in_grid = findValueIndexInArray(grid_steps[0], vec_start[0]) != findValueIndexInArray(grid_steps[0], vec_end[0])
    y_in_grid = findValueIndexInArray(grid_steps[1], vec_start[1]) != findValueIndexInArray(grid_steps[1], vec_end[1])
    return x_in_grid and y_in_grid

## grid functions ##
# generate xy-grid and initialize z-values with specified value
def makeXYZGrid(lim_x, lim_y, grid_size, init_z):
    steps_x = math.ceil(lim_x / grid_size)
    steps_y = math.ceil(lim_y / grid_size)
    grid_steps_x = npy.linspace(-steps_x * grid_size, steps_x * grid_size, steps_x * 2 + 1)
    grid_steps_y = npy.linspace(-steps_y * grid_size, steps_y * grid_size, steps_y * 2 + 1)
    grid_x, grid_y = npy.meshgrid(grid_steps_x, grid_steps_y)
    grid_z = npy.ones((steps_y * 2 + 1, steps_x * 2 + 1)) * init_z
    return grid_x, grid_y, grid_z, grid_steps_x, grid_steps_y

# get x and y ticks of a subgrid and offset compared to original grid
def getXYSubGridSteps(gridStepsX, gridStepsY, vecStart, vecEnd):
    xMin, xMax = min(vecStart[0], vecEnd[0]), max(vecStart[0], vecEnd[0])
    yMin, yMax = min(vecStart[1], vecEnd[1]), max(vecStart[1], vecEnd[1])
    offsetXMin = findValueIndexInArray(gridStepsX, xMin - globals.getConvUAMLatSep()) - 1
    offsetYMin = findValueIndexInArray(gridStepsY, yMin - globals.getConvUAMLatSep()) - 1
    offsetXMax = findValueIndexInArray(gridStepsX, xMax + globals.getConvUAMLatSep())
    offsetYMax = findValueIndexInArray(gridStepsY, yMax + globals.getConvUAMLatSep())
    return gridStepsX[offsetXMin:offsetXMax + 1], gridStepsY[offsetYMin:offsetYMax + 1], offsetXMin, offsetYMin

# get matrix of xy-coordinates of a subgrid, associated z-coordinates and offset compared to original grid
def getXYZSubGrids(vec_start, vec_end, padding, grid_steps, grid_xy, grid_z):
    x_min, x_max = min(vec_start[0], vec_end[0]), max(vec_start[0], vec_end[0])
    y_min, y_max = min(vec_start[1], vec_end[1]), max(vec_start[1], vec_end[1])
    offset_x_min = findValueIndexInArray(grid_steps[0], x_min - padding)
    offset_y_min = findValueIndexInArray(grid_steps[1], y_min - padding)
    offset_x_max = findValueIndexInArray(grid_steps[0], x_max + padding) + 1
    offset_y_max = findValueIndexInArray(grid_steps[1], y_max + padding) + 1
    if globals.debug:
        print(offset_x_min, offset_x_max, offset_y_min, offset_y_max)
    sub_grid_xy = grid_xy[offset_y_min:offset_y_max, offset_x_min:offset_x_max]
    sub_grid_z = grid_z[offset_y_min:offset_y_max, offset_x_min:offset_x_max]
    return sub_grid_xy, sub_grid_z, offset_x_min, offset_y_min

## misc ##
# get orthogonal distance of a point to a line
# in: vec_line = line to measure distance to [x dimension, y dimension], relation to point via vec_line_start2point -> [float, float]
#     vec_line_start2point = vector from start (or end) of line to point [x dimension, y dimension] -> [float, float]
# out: orthogonal distance -> float
def getPoint2VecOthoDist(vec_line, vec_line_start2point):
    return npy.abs(npy.cross(vec_line, vec_line_start2point))/norm(vec_line)



# get orthogonal distance of a point to a line with the sign
# in: vec_line = line to measure distance to [x dimension, y dimension], relation to point via vec_line_start2point -> [float, float]
#     vec_line_start2point = vector from start (or end) of line to point [x dimension, y dimension] -> [float, float]
# out: orthogonal distance -> float
def getPoint2VecOthoDistsign(vec_line, vec_line_start2point):
    return (npy.cross(vec_line, vec_line_start2point))/norm(vec_line)

# find index of last value lower than a certain value in an array of values
def findValueIndexInArray(array, value):
    result = npy.searchsorted(array, value)
    if result >= len(array):
        result = len(array) - 1
    return result

## conversions ##
# convert meters to feet
def convm2ft(val):
    return val * globals.factorm2ft

# convert feet to meter
def convft2m(val):
    return val/globals.factorm2ft

# convert nautical miles to meters
def convNM2m(val):
    return val * globals.factorNM2m
