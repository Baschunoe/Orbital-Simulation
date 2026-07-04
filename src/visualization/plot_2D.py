import sys
import numpy as np
from PyQt6 import QtCore

# Local imports
from src.physics.constants import EARTH_RADIUS, KM, G, EARTH_MASS
from src.visualization.helpers import load_arrays

def orbital_data_2D(trajectory3D, e, h, grav_accel_data3D):
    # -----------------------------
    # CONVERT TO 2D
    # -----------------------------

    trajectory2D = []
    
    direction_vector_x = e / np.linalg.norm(e)
    direction_vector_z = h / np.linalg.norm(h)
    direction_vector_y = np.cross(direction_vector_z, direction_vector_x)

    x2D_array = np.dot(trajectory3D, direction_vector_x)
    y2D_array = np.dot(trajectory3D, direction_vector_y)

    trajectory2D = np.column_stack((x2D_array, y2D_array))

    gx2D_array = np.dot(grav_accel_data3D, direction_vector_x)
    gy2D_array = np.dot(grav_accel_data3D, direction_vector_y)

    grav_accel_data2D = np.column_stack((gx2D_array, gy2D_array))
    
    return trajectory2D, grav_accel_data2D

    