# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 12:34:04 2023

@author: brian
"""

import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class HexagonalCell:
    def __init__(self, x, y, z, color):
        self.x = x
        self.y = y
        self.z = z
        self.color = color

def discretize_space(min_x, max_x, min_y, max_y, min_z, max_z, side_length, height):
    cells = []
    cell_width = side_length * 2
    cell_height = height
    
    # Calculate the vertical spacing between cells
    vertical_spacing = 1
    
    # Calculate the horizontal spacing between cells
    horizontal_spacing = 10
    
    # Calculate the spacing between layers
    layer_spacing = 0
    
    # Calculate the number of rows and columns
    num_columns = math.ceil((max_x - min_x) / horizontal_spacing) + 1
    num_rows = math.ceil((max_y - min_y) / vertical_spacing) + 1
    num_layers = math.ceil((max_z - min_z) / vertical_spacing) + 1
    
    # Calculate the color step size for each layer
    color_step = 1.0 / num_layers
    
    for layer in range(num_layers):
        for row in range(num_rows):
            for column in range(num_columns):
                """
                if row % 2 == 0:
                    x = min_x + column * horizontal_spacing
                else:
                    x = min_x + column * horizontal_spacing + horizontal_spacing / 2
                """    
                x = min_x + column * horizontal_spacing
                y = min_y + row * vertical_spacing
                z = min_z + layer * layer_spacing 
    
                # Calculate the color for the cell based on the layer
                color = layer * color_step
                
                cell = HexagonalCell(x, y, z, color)
                cells.append(cell)
                
    return cells

def visualize_cells(cells):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    x_values = [cell.x for cell in cells]
    y_values = [cell.y for cell in cells]
    z_values = [cell.z for cell in cells]
    colors = [cell.color for cell in cells]
    
    ax.scatter(x_values, y_values, z_values, c=colors, cmap='rainbow')
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    plt.show()

# Example usage:
min_x = 0
max_x = 100
min_y = 0
max_y = 100
min_z = 0
max_z = 100
side_length = 10
height = 10

cells = discretize_space(min_x, max_x, min_y, max_y, min_z, max_z, side_length, height)

visualize_cells(cells)
