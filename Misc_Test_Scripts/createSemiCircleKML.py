import math
import xml.etree.ElementTree as ET

def calculate_semi_circle(lat, lon, radius, direction, num_points=50):
    points = []
    start_angle = 0
    end_angle = 180
    if direction.lower() == 'left':
        start_angle, end_angle = end_angle, start_angle

    for i in range(num_points + 1):
        angle = math.radians(start_angle + (end_angle - start_angle) * i / num_points)
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        new_lat = lat + (dy / 110540)  # Approximation for conversion of degrees to meters
        new_lon = lon + (dx / (111320 * math.cos(math.radians(lat))))  # Correction for Earth's curvature
        points.append((new_lat, new_lon))
    
    return points

def create_kml(points, file_name):
    kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    document = ET.SubElement(kml, 'Document')
    placemark = ET.SubElement(document, 'Placemark')
    line_string = ET.SubElement(placemark, 'LineString')
    coordinates = ET.SubElement(line_string, 'coordinates')
    coordinates.text = ' '.join([f'{lon},{lat},0' for lat, lon in points])

    tree = ET.ElementTree(kml)
    tree.write(file_name)

# Example usage
start_lat, start_lon = 48.3014, 11.9069  # Replace with your start coordinates
radius = 1000  # in meters
direction = 'right'  # 'left' or 'right'
points = calculate_semi_circle(start_lat, start_lon, radius, direction)
create_kml(points, 'semicircle.kml')
