#####
# Imports data from Excel file
#####

import globals
import numpy as npy
import pandas as pnd
import helperFunctions as util
from PIL import Image
from classes import Waypoint, Threshold, InstrumentDeparture, Approach

def importExcelData(url):
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

def importPopulationMap(tile_urls, grid_size):  # only for data from https://download.geoservice.dlr.de/WSF2019/#details
    # specific for WSF2019 tiles
    tile_coverage_px = 22487
    tile_coverage_deg = 2
    tile_overlap_deg = 0.01
    tile_px_per_deg = tile_coverage_px / (tile_coverage_deg + 2 * tile_overlap_deg)
    tile_delta_xy_per_px = npy.array(util.coordLatLon2XY(abs(globals.referenceCoordLatLon[0]), abs(globals.referenceCoordLatLon[1]),
                                               abs(globals.referenceCoordLatLon[0]) + (tile_coverage_deg + 2 * tile_overlap_deg),
                                               abs(globals.referenceCoordLatLon[1]) + (tile_coverage_deg + 2 * tile_overlap_deg)))\
                           / tile_coverage_px
    tile_overlap_px = tile_px_per_deg * tile_overlap_deg

    tiles = importImages(tile_urls, npy.ceil(tile_overlap_px))
    (tile_width, tile_height) = tiles[0].size
    tile_coordinate_lowerleft = tile_urls[grid_size[1] - 1].removesuffix(".tif").split("_")
    result = Image.new("1", (int(grid_size[0] * tile_width), int(grid_size[1] * tile_height)))
    for index_width in range(0, grid_size[0] + 1, grid_size[1]):
        result.paste(im=tiles[index_width], box=(int(index_width / grid_size[1]) * tile_width, 0))
        for index_height in range(1, grid_size[1], grid_size[0]):
            result.paste(im=tiles[index_width + index_height],
                         box=(int(index_width / grid_size[1]) * tile_width, index_height * tile_height))

    tile_coordinate_lowerleft_xy = util.coordLatLon2XY(globals.referenceCoordLatLon[0], globals.referenceCoordLatLon[1],
                                                       int(tile_coordinate_lowerleft[-1]),
                                                       int(tile_coordinate_lowerleft[-2]))
    margin_top = (result.height - ((abs(tile_coordinate_lowerleft_xy[1]) + globals.grid_y_dim) / tile_delta_xy_per_px[1]))
    margin_left = (abs(tile_coordinate_lowerleft_xy[0]) - globals.grid_x_dim) / tile_delta_xy_per_px[0]
    boxcrop = (margin_left, margin_top, 2 * globals.grid_x_dim / tile_delta_xy_per_px[0] + margin_left,
               2 * globals.grid_y_dim / tile_delta_xy_per_px[1] + margin_top)
    result = result.crop(box=boxcrop)
    globals.map_population = npy.array(result.getdata()).reshape(result.height, result.width)
    steps_x = result.width / 2
    steps_y = result.height / 2
    grid_steps_x = npy.linspace(-steps_x * tile_delta_xy_per_px[0], steps_x * tile_delta_xy_per_px[0], int(steps_x * 2))
    grid_steps_y = npy.linspace(steps_y * tile_delta_xy_per_px[1], -steps_y * tile_delta_xy_per_px[1], int(steps_y * 2))
    a, b = \
        npy.meshgrid(grid_steps_x, grid_steps_y)
    c = npy.array(list(result.getdata())) / 255
    globals.map_population_grid_x = a.reshape(-1)[c != 0]
    globals.map_population_grid_y = b.reshape(-1)[c != 0]

def importImages(image_urls, crop_edge = 0):
    Image.MAX_IMAGE_PIXELS = 510000000 #WSF2019 images have 505665169 pixels (22487 x 22487)
    result = []
    for url in image_urls:
        image = Image.open(url)
        image = image.crop(box=(crop_edge, crop_edge, image.size[0] - crop_edge, image.size[1] - crop_edge))
        result.append(image)
    return result
