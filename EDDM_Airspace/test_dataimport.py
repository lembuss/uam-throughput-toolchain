import sys
import globals
import numpy as npy
import pandas as pnd
import helperFunctions as util
from PIL import Image
from classes import Waypoint, Threshold, InstrumentDeparture, Approach


def splitRouteList(type):
    for index, data_row in data.iterrows():
        if len(str(data_row[0])) > 3:
            if 'name' in locals():
                if type == 'Apch':
                    Approach(name=name, gradient=gradient, waypoints=waypoints, remarks=remarks, name_type=type)
                else:
                    InstrumentDeparture(name=name, gradient=gradient, waypoints=waypoints, remarks=remarks, name_type=type)
            name = data_row[0]
            gradient = data_row[1]
            waypoints = [data_row[2]]
            remarks = [data_row[3]]
        else:
            waypoints.append(data_row[2])
            remarks.append(data_row[3])
    if 'name' in locals():
        if type == 'Apch':
            Approach(name=name, gradient=gradient, waypoints=waypoints, remarks=remarks, name_type=type)
        else:
            InstrumentDeparture(name=name, gradient=gradient, waypoints=waypoints, remarks=remarks, name_type=type)

globals.init()
url = r'C:\Users\brian\OneDrive\Documents\TUM - MS Aerospace\Semester Thesis\Reinish Work\Abgabe LS-MA-22-09-Reinisch-Felix-03690057\03_Data\01_Programs\WPy64-31050\Dateien\EDDM\Input_Data\EDDM_STARs_SIDs_Waypoints_RF_no_crossing_UAV_Approach.xlsx'
data_sheets = pnd.read_excel(url, sheet_name=None)

for sheet_name, data in data_sheets.items():
    if sheet_name == 'Coordinates':
        # set reference point to waypoint named "Airport Ref"
        reference = data.loc[data['Waypoint'] == 'Airport Ref']
        globals.referenceCoordLatLon = [util.coordDeg2LatLon(reference.iat[0, 1]), util.coordDeg2LatLon(reference.iat[0, 2])]
        for _, sheet_data in data.iterrows():
            if sheet_data[0][0:3] == 'RWY':
                instance = Threshold(name=sheet_data[0], degNS=sheet_data[1], degEW=sheet_data[2], altitude=float(sheet_data[3]))
            else:
                instance = Waypoint(name=sheet_data[0], degNS=sheet_data[1], degEW=sheet_data[2])
            globals.waypoints[sheet_data[0]] = instance
        Threshold.calcOrientations()
    elif sheet_name == 'Approaches':
        splitRouteList('Apch')
    elif sheet_name[0:3] == 'SID':
        splitRouteList(sheet_name)
    else:
        print("Unused sheet in Excel file. Valid sheet names: 'Coordinates', 'Approaches' and 'SID xxx'")