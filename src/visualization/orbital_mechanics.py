import sys
import numpy as np
from PyQt6 import QtCore

# Local imports
from src.physics.constants import EARTH_RADIUS, KM, G, EARTH_MASS
from src.visualization.helpers import load_arrays

def orbital_mechanics(trajectory3D, distance):  
    # -----------------------------
    # 3. ORBITAL MECHANICS 
    # -----------------------------
    index_peri = np.argmin(distance) 
    index_apo = np.argmax(distance)

    vec_peri = trajectory3D[index_peri] 
    perigee = np.linalg.norm(vec_peri) - EARTH_RADIUS * KM
    vec_apo = trajectory3D[index_apo]
    apogee = np.linalg.norm(vec_apo) - EARTH_RADIUS * KM

    major_axis_vec = vec_apo - vec_peri 
    a = np.linalg.norm(major_axis_vec) / 2.0 

    center = vec_peri + major_axis_vec / 2.0
    xc, yc = center[0], center[1]

    c = np.linalg.norm(center) 
    b = np.sqrt(max(0, a**2 - c**2)) 

    theta = np.arctan2(vec_peri[1], vec_peri[0]) 
    e = c/a 

    print(f"Calculated True Orbital parameters:\n Center: ({xc:.2f}, {yc:.2f}) km\n Semi-major axis: {a:.2f} km\n Semi-minor axis: {b:.2f} km\n Rotation angle: {np.degrees(theta):.2f}°")

    diffs = np.diff(trajectory3D, axis=0)
    step_lengths = np.linalg.norm(diffs, axis=1)
    s = np.insert(np.cumsum(step_lengths), 0, 0)
    angle = s / s[-1]

    orbit_period = 2 * np.pi * np.sqrt(((a * 1000)**3) / (G * EARTH_MASS))

    return perigee, apogee, a, b, xc, yc, theta, e, angle, orbit_period