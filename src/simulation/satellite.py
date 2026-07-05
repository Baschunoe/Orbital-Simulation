import numpy as np
from src.physics.constants import EARTH_RADIUS

class Satellite:
    def __init__(self, position, velocity):
        
        # -----------------------------
        # INITIALIZE STATE
        # -----------------------------
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        
        # Calculate these once during initialization/updates
        self.radius = np.linalg.norm(self.position)
        self.distance_from_earth = self.radius - EARTH_RADIUS

    def update_state(self, position, velocity):
        
        # -----------------------------
        # UPDATE STATE
        # -----------------------------
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.radius = np.linalg.norm(self.position)
        self.distance_from_earth = self.radius - EARTH_RADIUS