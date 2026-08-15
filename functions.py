import math
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import numpy as np


def convert_ft_to_nm (feet):
    return feet / 6076.11549

def convert_nm_to_ft (nautical_miles):
    return nautical_miles * 6076.11549

def convert_nm_to_m (nautical_miles):
    return nautical_miles * 1852

def convert_m_to_nm (meters):
    return meters / 1852

def convert_ft_to_m (feet):
    return feet / 3.281

def convert_m_to_ft (meters):
    return meters * 3.281

def convert_knots_to_kmh (knots):
    return knots / 1.852

def convert_kmh_to_knots (kmh):
    return kmh * 1.852

def reciprocal_heading(heading):
        if heading >= 180:
            return heading - 180
        elif heading < 180:
            return heading + 180
        
def adjust_for_restrictedareas(bearing):
    return bearing + 3
    #return bearing

def compute_heading(heading1, heading2, computation):
    heading = heading1 - heading2 if computation == 'subtract' else heading1 + heading2
    return heading % 360
    
def calculate_new_position(lat, lon, brng, dist_nm, altitude_m):
        # Radius of the Earth in kilometers
        R = 6371.01
        # Convert bearing to radians and distance to kilometers
        brng = math.radians(brng)
        dist_km = convert_nm_to_m(dist_nm) / 1000

        # Convert latitude and longitude to radians
        lat1 = math.radians(lat)
        lon1 = math.radians(lon)

        # Calculate new latitude
        lat2 = math.asin(math.sin(lat1) * math.cos(dist_km / R) + math.cos(lat1) * math.sin(dist_km / R) * math.cos(brng))

        # Calculate new longitude
        lon2 = lon1 + math.atan2(math.sin(brng) * math.sin(dist_km / R) * math.cos(lat1), math.cos(dist_km / R) - math.sin(lat1) * math.sin(lat2))

        # Convert back to degrees
        return math.degrees(lat2), math.degrees(lon2), altitude_m

def distance_between_two_points(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0
    coord1 = (lat1, lon1)
    coord2 = (lat2, lon2)

    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)

    # Difference in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c
    return convert_m_to_nm(distance*1000)

def calculate_segment_glideslope_nm(runway_elevation_ft, altitude_ft, glideslope_angle_deg):
    glideslope_angle_rad = math.radians(glideslope_angle_deg)

    difference_altitude_ft = altitude_ft -runway_elevation_ft
    segment_distance_nm = convert_ft_to_nm(difference_altitude_ft/ math.tan(glideslope_angle_rad))

    return segment_distance_nm

def calculate_altitude_glideslope_ft(runway_elevation_ft, distance_from_threshold_nm, glideslope_angle_deg):
    glideslope_angle_rad = math.radians(glideslope_angle_deg)

    point_altitude_ft = convert_nm_to_ft(distance_from_threshold_nm * math.tan(glideslope_angle_rad))

    return point_altitude_ft + runway_elevation_ft

def create_path_kml(filename, coordinates):
    kml = Element('kml')
    kml.set('xmlns', 'http://www.opengis.net/kml/2.2')
    document = SubElement(kml, 'Document')
    
    placemark = SubElement(document, 'Placemark')
    linestring = SubElement(placemark, 'LineString')

    # Set altitudeMode to 'absolute'
    altitude_mode = SubElement(linestring, 'altitudeMode')
    altitude_mode.text = 'absolute'

    coordinates_tag = SubElement(linestring, 'coordinates')
    coordinates_tag.text = ' '.join([f"{lon},{lat},{alt}" for lat, lon, alt in coordinates])
    
    xml_str = minidom.parseString(tostring(kml)).toprettyxml(indent="   ")
    with open(filename, "w") as f:
        f.write(xml_str)

def create_placemarks_kml(filename, coordinates, labels):
    if len(coordinates) != len(labels):
        raise ValueError("The number of coordinates must match the number of labels")

    kml = Element('kml')
    kml.set('xmlns', 'http://www.opengis.net/kml/2.2')
    document = SubElement(kml, 'Document')

    # Create waypoints
    for (lat, lon, alt), label in zip(coordinates, labels):
        placemark = SubElement(document, 'Placemark')
        point = SubElement(placemark, 'Point')
        coordinate = SubElement(point, 'coordinates')
        coordinate.text = f"{lon},{lat},{alt}"

        altitudeMode = SubElement(point, 'altitudeMode')
        altitudeMode.text = 'absolute'  # Set altitude mode to absolute

        name = SubElement(placemark, 'name')
        name.text = label

    xml_str = minidom.parseString(tostring(kml)).toprettyxml(indent="   ")
    with open(filename, "w") as f:
        f.write(xml_str)

def create_restricted_area_kml(filename, corners):
    kml = Element('kml')
    kml.set('xmlns', 'http://www.opengis.net/kml/2.2')
    document = SubElement(kml, 'Document')

    # Add Style for the Polygon
    style = SubElement(document, 'Style')
    style.set('id', 'lightRedPoly')
    poly_style = SubElement(style, 'PolyStyle')
    color = SubElement(poly_style, 'color')
    color.text = 'ff9999ff'  # Light red color

    placemark = SubElement(document, 'Placemark')
    placemark.append(style)  # Reference the defined style

    polygon = SubElement(placemark, 'Polygon')
    
    # Set extrude to '1' to extend the shape to the ground
    extrude = SubElement(polygon, 'extrude')
    extrude.text = '1'

    # Set altitudeMode to 'absolute'
    altitude_mode = SubElement(polygon, 'altitudeMode')
    altitude_mode.text = 'absolute'

    outer_boundary_is = SubElement(polygon, 'outerBoundaryIs')
    linear_ring = SubElement(outer_boundary_is, 'LinearRing')

    coordinates_tag = SubElement(linear_ring, 'coordinates')
    coordinates_tag.text = ' '.join([f"{lon},{lat},{alt}" for lat, lon, alt in corners])
    
    xml_str = minidom.parseString(tostring(kml)).toprettyxml(indent="   ")
    with open(filename, "w") as f:
        f.write(xml_str)
        
def find_child_with_attribute(parent_class, attribute_value, attribute):
    for subclass in parent_class.__subclasses__():
        instance = subclass()
        if hasattr(instance, attribute) and getattr(instance, attribute) == attribute_value:
            return subclass
    return None