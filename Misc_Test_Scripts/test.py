# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 14:52:02 2023

@author: brian
"""

import matplotlib.pyplot as plt

# Sample data
x = [1, 2, 3, 4, 5]
y = [10, 20, 30, 40, 50]

# Y-value where you want to draw the vertical line
vertical_line_y = 25

# Create the plot
plt.plot(x, y)

# Draw the vertical line at the specified y-value
plt.axvline(x=vertical_line_y, color='red', linestyle='--', label=f'Vertical Line at y={vertical_line_y}')

# Customize the plot
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title(f'Plot with Vertical Line at y={vertical_line_y}')
plt.legend()

# Show the plot
plt.show()
