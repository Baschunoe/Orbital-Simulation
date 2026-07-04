import sys
import numpy as np
from PyQt6 import QtCore

# Local imports
from src.physics.constants import EARTH_RADIUS, KM, G, EARTH_MASS
from src.visualization.helpers import load_arrays

def orbital_mechanics(trajectory3D, distance):  
    # -----------------------------
    # ORBITAL MECHANICS 
    # -----------------------------
    index_peri = np.argmin(distance) 
    index_apo = np.argmax(distance)

    vec_peri = trajectory3D[index_peri] 
    perigee = np.linalg.norm(vec_peri) - EARTH_RADIUS * KM
    vec_apo = trajectory3D[index_apo]
    apogee = np.linalg.norm(vec_apo) - EARTH_RADIUS * KM

    major_axis_vec = vec_apo - vec_peri 
    a = np.linalg.norm(major_axis_vec) / 2.0 

    # 3D Center Coordinates
    center = vec_peri + major_axis_vec / 2.0
    xc, yc, zc = center[0], center[1], center[2]

    c = np.linalg.norm(center) 
    b = np.sqrt(max(0, a**2 - c**2)) 

    # 3D Orientation of the perigee (Azimuth and Elevation)
    theta_xy = np.arctan2(vec_peri[1], vec_peri[0]) 
    phi_z = np.arcsin(vec_peri[2] / np.linalg.norm(vec_peri)) if np.linalg.norm(vec_peri) != 0 else 0
    
    e = c / a if a != 0 else 0
    e_vector = e * (vec_peri / np.linalg.norm(vec_peri)) if np.linalg.norm(vec_peri) != 0 else np.zeros(3)

    print(f"Calculated True Orbital parameters:\n"
          f" Center: ({xc:.2f}, {yc:.2f}, {zc:.2f}) km\n"
          f" Semi-major axis: {a:.2f} km\n"
          f" Semi-minor axis: {b:.2f} km\n"
          f" Periapsis Azimuth (XY): {np.degrees(theta_xy):.2f}°\n"
          f" Periapsis Elevation (Z): {np.degrees(phi_z):.2f}°")

    diffs = np.diff(trajectory3D, axis=0)
    step_lengths = np.linalg.norm(diffs, axis=1)
    s = np.insert(np.cumsum(step_lengths), 0, 0)
    
    # Safety check to avoid division by zero
    if s[-1] != 0:
        arc_progress = s / s[-1]
    else:
        arc_progress = np.zeros_like(s)

    orbit_period = 2 * np.pi * np.sqrt(((a * 1000)**3) / (G * EARTH_MASS))

    # Returning the updated variables: zc, theta_xy, phi_z, and your renamed arc_progress
    return perigee, apogee, a, b, xc, yc, zc, theta_xy, phi_z, e, e_vector, arc_progress, orbit_period