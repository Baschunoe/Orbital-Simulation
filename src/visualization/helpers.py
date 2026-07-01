import sys
import numpy as np
from PyQt6 import QtCore

# Local imports
from src.physics.constants import EARTH_RADIUS, KM, G, EARTH_MASS

def load_arrays(sat, step, dt):
    trajectory3D = []
    distance = []
    velocity = []
    
    start_x, start_y, start_z = sat.position
    iterations = 0

    print("Simulating orbit... Please wait.")
    while True:
        iterations += 1
        step(sat, dt) 
        sat.update_distance()

        trajectory3D.append(sat.position.copy() * KM)
        distance.append(sat.distance_from_earth * KM)
        velocity.append(sat.velocity.copy())
        
        if np.allclose(sat.position, [start_x, start_y, start_z], atol=10000) and iterations > 1:
            print(f"Orbit completed after {iterations} iterations.")
            break
        elif np.linalg.norm(sat.position) <= EARTH_RADIUS:
            print(f"Satellite has crashed into Earth after {iterations} iterations.")
            break
        if iterations > 10000000:
            print("Max iterations reached.")
            break

    trajectory3D = np.array(trajectory3D)
    distance = np.array(distance)
    velocity = np.array(velocity)

    return trajectory3D, distance, velocity

def telemetry(trajectory3D, distance, velocity, dt):
    print("Calculating telemetry arrays...")
    
    time_data = np.arange(len(trajectory3D)) * dt
    v_ms_data = np.linalg.norm(velocity, axis=1) 
    speed_data = v_ms_data / 1000                
    speed_kmh_data = speed_data * 3600           
    
    r_meters_data = distance * 1000 + EARTH_RADIUS
    
    energy_j_kg_data = (v_ms_data**2 / 2) - ((G * EARTH_MASS) / r_meters_data)
    energy_mj_kg_data = energy_j_kg_data / 1_000_000
    
    momentum_data = np.abs(np.cross(trajectory3D * 1000, velocity)) # Attention when switching to 3d - cross gives a vector in 3d instead of a z scalar
    
    g_mag_data = (G * EARTH_MASS) / (r_meters_data**2)
    unit_vector_data = (-trajectory3D * 1000) / r_meters_data[:, np.newaxis] 
    grav_accel_data = g_mag_data[:, np.newaxis] * unit_vector_data
    grav_accel_norm_data = np.linalg.norm(grav_accel_data, axis=1)

    return time_data, speed_data, speed_kmh_data, energy_mj_kg_data, momentum_data, grav_accel_data, grav_accel_norm_data

    