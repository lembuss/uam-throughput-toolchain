import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from shapely.geometry import LineString

# Load the data from the GeoJSON file
with open('20230527-plotairbus.geojson') as f:
    data = json.load(f)

# Extract the coordinates for each linestring
lines = []
for feature in data['features']:
    coords = feature['geometry']['coordinates']
    z = feature['properties']['value']
    line = LineString(coords)
    lines.append((line,z))

# Create a 3D plot of the lines
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for line, z in lines:
    x, y = line.coords.xy
    ax.plot(x, y, z)

# Set the axis labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Plot')

# Show the plot
plt.show()