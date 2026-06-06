from src.simulation.satellite import Satellite
from src.simulation.propagator import step
from src.visualization.plot_2D import plot_orbit

trajectory = []

sat = Satellite(

    position=[7000000, 0],

    velocity=[0,9000]
)

dt = 0.1

for i in range(200000):

    trajectory.append(
        sat.position.copy()
    )

    step(sat, dt)

plot_orbit(trajectory)