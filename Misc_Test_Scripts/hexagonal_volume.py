# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 13:26:39 2023

@author: brian
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define the points of the hexagon base
radius = 1.0  # Radius of the circumscribed circle of the hexagon
angle = np.linspace(0, 2*np.pi, 7)[:-1]  # Angles for the vertices of the hexagon
x = radius * np.cos(angle)
y = radius * np.sin(angle)

# add last coordinates for x and y. 

x = np.append(x, x[0])
y = np.append(y, y[0])
z_base = 0  # Base height of the hexagonal prism

# Define the heights of the top and bottom faces
z_top = 2  # Height of the top face
z_bottom = 0  # Height of the bottom face

# Create the figure and the 3D axis
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the hexagonal prism
#ax.add_collection3d(plt.Polygon(list(zip(x, y)), closed=True, alpha=0.5))
#ax.add_collection3d(plt.Polygon(list(zip(x, y)), closed=True, alpha=0.5, zdir='z', zs=z_top))
ax.plot(x, y, [z_top]*7, color='k', linewidth=1)
ax.plot(x, y, [z_bottom]*7, color='k', linewidth=1)

# Set axis labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Set plot limits
ax.set_xlim([-radius, radius])
ax.set_ylim([-radius, radius])
ax.set_zlim([0, z_top])

# Show the plot
plt.show()
