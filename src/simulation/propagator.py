import numpy as np
from src.physics.gravity import gravitational_acceleration

def step(satellite, dt):
    
    pos = satellite.position
    vel = satellite.velocity
    
    # Helper to get velocity and acceleration
    def get_derivatives(p, v):
        # Return velocity (dp/dt) and acceleration (dv/dt)
        return v, gravitational_acceleration(p)

    # RK4 Step 1
    v1, a1 = get_derivatives(pos, vel)
    
    # RK4 Step 2
    v2, a2 = get_derivatives(pos + v1 * dt / 2, vel + a1 * dt / 2)
    
    # RK4 Step 3
    v3, a3 = get_derivatives(pos + v2 * dt / 2, vel + a2 * dt / 2)
    
    # RK4 Step 4
    v4, a4 = get_derivatives(pos + v3 * dt, vel + a3 * dt)

    # Calculate final state
    satellite.position = pos + (dt / 6.0) * (v1 + 2*v2 + 2*v3 + v4)
    satellite.velocity = vel + (dt / 6.0) * (a1 + 2*a2 + 2*a3 + a4)