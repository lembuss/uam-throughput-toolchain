import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from shapely.geometry import LineString
import helperFunctions as util
import numpy as npy

# # Load the data from the GeoJSON file
# with open('plot.geojson') as f:
#     data = json.load(f)

# # Extract the coordinates for each linestring
# lines = []
# for feature in data['features']:
#     coords = feature['geometry']['coordinates']
#     z = feature['properties']['value']
#     line = LineString(coords)
#     lines.append((line,z))

# # Create a 3D plot of the lines
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# for line, z in lines:
#     x, y = line.coords.xy
#     ax.plot(x, y, z)

# # Set the axis labels and title
# ax.set_xlabel('X')
# ax.set_ylabel('Y')
# ax.set_zlabel('Z')
# ax.set_title('3D Plot')

# # Set the limits of the x, y, and z axes

# ax.set_xlim([-40000, 40000])
# ax.set_ylim([-30000, 30000])
# ax.set_zlim([1400, 5000])


# # Show the plot
# plt.show()

Minput = npy.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]])
print("Minput", Minput)
vec_segment=  npy.array([2,2])
slidedM = util.slide_elevation_matrix08(Minput, 6, 2, vec_segment)

print('slided M', slidedM)