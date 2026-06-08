import numpy as np
from src.physics.constants import EARTH_RADIUS

class Satellite:

    def __init__(self, position, velocity, distance_from_earth, angle):

        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.distance_from_earth = np.array(distance_from_earth, dtype=float)
        self.angle = np.array(angle, dtype=float)

    def update_distance(self):

        self.distance_from_earth = np.linalg.norm(self.position) - EARTH_RADIUS

        return self.distance_from_earth
    
    @staticmethod
    def update_angle(x, y, cx, cy):

        angle = np.degrees(np.arctan2(y - cy, x - cx)) % 360

        return angle