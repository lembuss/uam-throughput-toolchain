from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def create_restricted_area_kml(filename, corners):
    kml = Element('kml')
    kml.set('xmlns', 'http://www.opengis.net/kml/2.2')
    document = SubElement(kml, 'Document')
    
    placemark = SubElement(document, 'Placemark')
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