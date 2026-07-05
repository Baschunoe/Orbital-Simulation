import numpy as np
from src.physics.constants import EARTH_RADIUS
from src.simulation.satellite import Satellite
from src.visualization.layout import start_application

start_x = EARTH_RADIUS + 427000
start_y = 0
start_z = 0

sat = Satellite(
    position=[start_x, start_y, start_z],
    velocity=[100, 7000, 5997]
)

dt = 1

start_application(sat, dt)