import openpyxl
import pandas as pd
import simplekml
from datetime import timedelta
import geopandas as gpd
import get_aircraft_data
from aircraft_categories import AircraftCatalog

# Function to convert GeoJSON to KML
def convert_geojson_to_kml(geojson_file, kml, start_time, end_time):
    gdf = gpd.read_file(geojson_file)
    for _, row in gdf.iterrows():
        if row.geometry.type == 'Point':
            pnt = kml.newpoint(name="GeoJSON Point", coords=[(row.geometry.x, row.geometry.y)])
        elif row.geometry.type == 'LineString':
            linestring = kml.newlinestring(name="GeoJSON Line", coords=row.geometry.coords[:])
        # Add other geometry types as needed

        # Set the time span for this geometry
        pnt.timespan.begin = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        pnt.timespan.end = end_time.strftime('%Y-%m-%dT%H:%M:%S')



