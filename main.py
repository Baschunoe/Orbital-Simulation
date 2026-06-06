from numpy import atan2
import numpy as np

from src.physics.constants import EARTH_RADIUS
from src.simulation.satellite import Satellite
from src.simulation.propagator import step
from src.visualization.plot_2D import animate_orbit


start_x = 7000000
start_y = 0
start_angle = atan2(start_y, start_x)

sat = Satellite(
    position=[start_x, start_y],
    velocity=[0, 8000]
)

dt = 10


# 🚀 ONLY THIS RUNS
animate_orbit(sat, step, dt)