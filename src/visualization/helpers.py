import numpy as np
from src.physics.constants import EARTH_RADIUS, KM, G, EARTH_MASS
from src.simulation.propagator import propagate_orbit_rk45

# -----------------------------
# EXACT ORBIT PERIOD
# -----------------------------
def calculate_orbit_period(pos, vel):
    
    r = np.linalg.norm(pos)
    v = np.linalg.norm(vel)
    
    # Specific orbital energy
    epsilon = (v**2 / 2) - (G * EARTH_MASS / r)
    
    if epsilon >= 0:
        return 1000000 
        
    a = - (G * EARTH_MASS) / (2 * epsilon)
    period = 2 * np.pi * np.sqrt((a**3) / (G * EARTH_MASS))
    
    return period

# -----------------------------
# LOAD ARRAYS
# -----------------------------
def load_arrays(sat, dt):
    
    # Calculate exact period to avoid infinite loops
    period = calculate_orbit_period(sat.position, sat.velocity)
    max_time = period
    
    # Run RK45 Propagator
    positions, velocities = propagate_orbit_rk45(sat, dt, max_time)
    
    # Scale for visualization
    trajectory3D = positions * KM
    distances = np.linalg.norm(positions, axis=1)
    distance_from_earth = (distances - EARTH_RADIUS) * KM
    
    return trajectory3D, distance_from_earth, velocities

# -----------------------------
# TELEMETRY
# -----------------------------
def telemetry(trajectory3D, distance, velocity, dt):
    
    print("Calculating telemetry arrays...")
    
    time_data = np.arange(len(trajectory3D)) * dt
    v_ms_data = np.linalg.norm(velocity, axis=1) 
    speed_data = v_ms_data / 1000                
    speed_kmh_data = speed_data * 3600           
    
    r_meters_data = distance * 1000 + EARTH_RADIUS
    
    energy_j_kg_data = (v_ms_data**2 / 2) - ((G * EARTH_MASS) / r_meters_data)
    energy_mj_kg_data = energy_j_kg_data / 1_000_000
    
    h_vectors = np.cross(trajectory3D * 1000, velocity)
    momentum_data = np.linalg.norm(h_vectors, axis=1)
    h = h_vectors[0]
    
    g_mag_data = (G * EARTH_MASS) / (r_meters_data**2)
    unit_vector_data = (-trajectory3D * 1000) / r_meters_data[:, np.newaxis] 
    grav_accel_data3D = g_mag_data[:, np.newaxis] * unit_vector_data
    grav_accel_norm_data = np.linalg.norm(grav_accel_data3D, axis=1)

    return time_data, speed_data, speed_kmh_data, energy_mj_kg_data, momentum_data, grav_accel_data3D, grav_accel_norm_data, h