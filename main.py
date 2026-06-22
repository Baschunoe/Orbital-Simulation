from numpy import atan2
import numpy as np

from src.physics.constants import EARTH_RADIUS
from src.simulation.satellite import Satellite
from src.simulation.propagator import step
# from src.visualization.plot_2D import animate_orbit
from src.visualization.plot import animate_orbit


start_x = EARTH_RADIUS + 408000
start_y = 0
start_angle = atan2(start_y, start_x)

sat = Satellite(
    position=[start_x, start_y],
    velocity=[0, 9000],
    distance_from_earth=np.linalg.norm([start_x, start_y]) - EARTH_RADIUS,
    angle=start_angle
)

dt = 1



animate_orbit(sat, step, dt)