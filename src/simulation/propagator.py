import numpy as np
import scipy.integrate
from src.physics.gravity import gravitational_acceleration
from src.physics.constants import EARTH_RADIUS

# -----------------------------
# PHYSICS MODEL FOR RK45
# -----------------------------
def physics_model(t, state):
    
    pos = state[:3]
    vel = state[3:]
    accel = gravitational_acceleration(pos)
    
    return np.concatenate((vel, accel))

# -----------------------------
# CRASH EVENT DETECTION
# -----------------------------
def crash_event(t, state):
    
    pos = state[:3]
    return np.linalg.norm(pos) - EARTH_RADIUS

# Tell SciPy to stop the integration if a crash happens
crash_event.terminal = True
crash_event.direction = -1

# -----------------------------
# PROPAGATOR RK45
# -----------------------------
def propagate_orbit_rk45(satellite, dt, max_time):
    
    print("Simulating orbit with RK45... Please wait.")
    
    initial_state = np.concatenate((satellite.position, satellite.velocity))
    
    # Generate points at exactly dt intervals for smooth animation
    t_eval = np.arange(0, max_time, dt)
    
    solution = scipy.integrate.solve_ivp(
        fun=physics_model,
        t_span=(0, max_time),
        y0=initial_state,
        method='RK45',
        t_eval=t_eval,
        events=[crash_event],
        rtol=1e-6, 
        atol=1e-9
    )
    
    # Extract arrays
    positions = solution.y[:3, :].T
    velocities = solution.y[3:, :].T
    
    if solution.status == 1:
        print(f"Simulation ended early: Satellite crashed at t={solution.t[-1]:.1f}s.")
    else:
        print(f"Simulation completed {len(solution.t)} frames.")
        
    return positions, velocities