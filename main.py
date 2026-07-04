from numpy import atan2
import numpy as np

from src.physics.constants import EARTH_RADIUS
from src.simulation.satellite import Satellite
from src.simulation.propagator import step
from src.visualization.layout import animate_orbit


start_x = EARTH_RADIUS + 427000
start_y = 0
start_z = 0
start_angle = 0 # fix later

sat = Satellite(
    position=[start_x, start_y, start_z],
    velocity=[0, 4755, 5997],
    distance_from_earth=np.linalg.norm([start_x, start_y, start_z]) - EARTH_RADIUS,
    angle=start_angle
)

dt = 1



animate_orbit(sat, step, dt)