import helperFunctions as util
import numpy as npy

# definition of global parameters
def init():
    global debug # show debug infos

    global grid_size # difference between search grid points (x and y direction) [m]
    global grid_x_dim # size of search grid in EW-direction, expanding to both sides from aerodrome reference coordinates[m]
    global grid_y_dim # size of search grid in NS-direction, expanding to both sides from aerodrome reference coordinates[m]
    # global sepHSID # required lateral distance to both sides of SIDs, equals track precision [m]
    # global sepHUAM # required lateral separation of UAM vehicle to conventional traffic [m]
    global sepHRadarVectoring # required lateral separation of UAM vehicle to conventional traffic (radar separation) [m]
    global sepVUAM # required vertical separation of UAM vehicle to conventional traffic [ft]
    global sepWakeTurb # required wake turbolence seperation from threshold [Nm]
    global sepParallelApch # required distance between indipendent parallel approaches
    global UAVDepCorridor # corridor width for UAV departures
    global stdGradient # standard climb gradient for SIDs [%]
    global stdGlidePath # standart glide path angle  
    global maxAltitude # maximum altitude aircraft on the SIDs fly at [ft]
    global maxAltitudeUAV
    global maxHeightUAM # maximum height the UAM vehicles fly at [ft]
    global refTerrain # terrain reference height [ft]
    global factorm2ft # conversion factor for meters to feet [ft per m]
    global factorNM2m  # conversion factor for NM to meters [m per NM]

    global waypoints # dictionary of waypoints, empty until imported; key = name | instance of class waypoint or threshold
    global referenceCoordLatLon # reference for xy-coordinates, auttomatically set to airport reference point
    global grid_x, grid_y, grid_z # coordinates (x,y) of search grid and values at the coordinates

    global map_population
    global map_population_grid_x, map_population_grid_y # coordinates of the population map grid

    global vec_start26C
    global vec_end26C
    global vec_start8C
    global vec_end8C
   

    debug = False

    grid_size = 100
    grid_x_dim = 44000 
    grid_y_dim = 32000 # increased from 22000 because part of the contoure data was not displayed 
    # sepHSID = 1000
    # sepHUAM = 1500
    sepHRadarVectoring = 5556 # 3 Nm Radar Separation Distance
    sepVUAM = 1000 # 1500ft
    sepWakeTurb = 12964  # 7 Nm
    sepParallelApch = 880 # Distance from conv RWYs to NOZ of UAV (NTZ 610 m + 0,5*NOZ conv traffic) 
    UAVDepCorridor = 780 
    stdGradient = 3.3
    stdGlidePath = 3 
    maxAltitude = 7000
    maxAltitudeUAV = 2500
    maxHeightUAM = 2000 #1500ft
    refTerrain = 1500 # changed from 1400 ft 
    factorm2ft = 3.28084
    factorNM2m = 1852

    vec_start26C = npy.array([-2963.569268156505, -342.5760821810361])
    vec_end26C = npy.array([-38455.317451927185, -4572.562843236562])
    vec_start8C = npy.array([-2873.371507100286, -332.1175778723717])
    vec_end8C = npy.array([34656.71598652721, 3891.5580812634444])
    
    

    waypoints = {}
    referenceCoordLatLon = []

    grid_x, grid_y, grid_z, _, _ = util.makeXYZGrid(grid_x_dim, grid_y_dim, grid_size, maxHeightUAM)

# getter methods for global variables
def getReferenceCood():
    return referenceCoordLatLon

def getWaypointList():
    return waypoints

def getConvUAMLatSep():
    return sepHRadarVectoring

def getConvUAMVSep():
    return sepVUAM

def getWakeTurbSep():
    CAT = 'Z'
    return getWakeTurbSepDynamic(CAT)
    #return sepWakeTurb

def getParallelApchSep():
    return sepParallelApch

def getUAVDepCorridor():
    return UAVDepCorridor

def getGridSize():
    return grid_size

def getXYGridVectorsAndZValues():
    grid_xy_vectors = npy.array([grid_x, grid_y]).transpose((1,2,0))
    return grid_xy_vectors, grid_z

def getXYGridAndZValues():
    return grid_x, grid_y, grid_z

def getXYGridDimensions():
    return [grid_x_dim, grid_y_dim]

def getXYGridSteps():
    grid_x_steps = grid_x[0]
    grid_y_steps = grid_y.transpose()[0]
    return [grid_x_steps, grid_y_steps]

## dynamic reconfiguration
def getWakeTurbSepDynamic(CAT):
    if CAT == 'A':
        sepWakeTurb = nautical_miles_to_meters(8)
    elif CAT == 'B':
        sepWakeTurb = nautical_miles_to_meters(7)
    elif CAT == 'C':
        sepWakeTurb = nautical_miles_to_meters(6)
    elif CAT == 'D':
        sepWakeTurb = nautical_miles_to_meters(5)
    elif CAT == 'E':
        sepWakeTurb = nautical_miles_to_meters(4)
    elif CAT == 'F':
        sepWakeTurb = nautical_miles_to_meters(3)
    elif CAT == 'Z':
        sepWakeTurb = nautical_miles_to_meters(2)
    return sepWakeTurb

def nautical_miles_to_meters(nautical_miles):
    # One nautical mile is approximately 1852 meters
    return nautical_miles * 1852
