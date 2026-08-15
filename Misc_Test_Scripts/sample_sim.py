import simplekml
import datetime

# Sample data: List of dictionaries with aircraft details
data = [
    {"category": "Commercial", "arrival_time": "2023-11-14T08:00:00Z", "latitude": 40.7128, "longitude": -74.0060},
    {"category": "Private", "arrival_time": "2023-11-14T09:00:00Z", "latitude": 34.0522, "longitude": -118.2437},
    # Add more entries as needed
]

# Create a KML object
kml = simplekml.Kml()

# Loop through the data to create placemarks
for aircraft in data:
    pnt = kml.newpoint(name=f"{aircraft['category']} Arrival")
    pnt.coords = [(aircraft['longitude'], aircraft['latitude'])]
    pnt.timestamp.when = aircraft['arrival_time']

    # You can customize the style based on the aircraft category
    if aircraft['category'] == "Commercial":
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/airports.png'
    else:
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/heliport.png'

# Save the KML to a file
kml.save("aircraft_arrivals.kml")

print("KML file created successfully.")
