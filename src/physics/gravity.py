import numpy as np

from src.physics.constants import G, EARTH_MASS

def gravitational_acceleration(position):

    r = np.linalg.norm(position)

    return - (G * EARTH_MASS) * (position/ r**3)