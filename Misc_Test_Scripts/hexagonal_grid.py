# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 15:05:56 2023

@author: brian
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def hex_prism_vertices(center, size):
    """
    Calculate the vertices of a hexagonal prism given its center and size.
    """
    x, y, z = center
    w = size
    h = size
    vertices = [
        (x - w/2, y - np.sqrt(3) * h/6, z - h/2),
        (x + w/2, y - np.sqrt(3) * h/6, z - h/2),
        (x + w, y, z - h/2),
        (x + w/2, y + np.sqrt(3) * h/6, z - h/2),
        (x - w/2, y + np.sqrt(3) * h/6, z - h/2),
        (x - w, y, z - h/2),
        (x - w/2, y - np.sqrt(3) * h/6, z + h/2),
        (x + w/2, y - np.sqrt(3) * h/6, z + h/2),
        (x + w, y, z + h/2),
        (x + w/2, y + np.sqrt(3) * h/6, z + h/2),
        (x - w/2, y + np.sqrt(3) * h/6, z + h/2),
        (x - w, y, z + h/2),
    ]
    return vertices

def plot_hex_prism(ax, center, size, color='blue'):
    """
    Plot a hexagonal prism given its center, size, and color.
    """
    vertices = np.array(hex_prism_vertices(center, size))
    faces = [
        [vertices[i] for i in [0, 1, 2, 3, 4, 5]], # bottom face
        [vertices[i] for i in [6, 7, 8, 9, 10, 11]], # top face
    ]

    for i in range(6):
        face = [vertices[i], vertices[i + 6], vertices[(i + 1) % 6 + 6], vertices[(i + 1) % 6]]
        faces.append(face)

    faces = np.array(faces)

    ax.add_collection3d(plt.Polygon(faces[0], color=color, alpha=0.6))
    ax.add_collection3d(plt.Polygon(faces[1], color=color, alpha=0.6))
    for i in range(6):
        ax.add_collection3d(plt.Polygon(faces[i + 2], color=color, alpha=0.6))

def plot_hexagonal_grid(size, num_rows, num_cols):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for row in range(num_rows):
        for col in range(num_cols):
            x = col * size * 1.5
            y = row * np.sqrt(3) * size + (col % 2) * np.sqrt(3) * size / 2
            z = 0
            center = (x, y, z)
            plot_hex_prism(ax, center, size)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()

# Example usage:
hex_size = 1.0
num_rows = 5
num_cols = 5
plot_hexagonal_grid(hex_size, num_rows, num_cols)
