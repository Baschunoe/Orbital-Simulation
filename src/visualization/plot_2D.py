import matplotlib.pyplot as plt
import numpy as np
from numpy import atan2
from matplotlib.ticker import MaxNLocator
from matplotlib import animation

from src.physics.constants import EARTH_RADIUS, KM


def plot_orbit(trajectory):

    trajectory = np.array(trajectory) * KM

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.plot(trajectory[:, 0], trajectory[:, 1], label="Trajectory")

    earth = plt.Circle(
        (0, 0),
        EARTH_RADIUS * KM,
        color='blue',
        alpha=0.5,
        label="Earth"
    )
    ax.add_patch(earth)

    ax.scatter(trajectory[-1, 0], trajectory[-1, 1], label="Satellite")

    limit = np.max(np.linalg.norm(trajectory, axis=1))
    scale = 1 + 1 / (1 + limit / 1e7)
    limit *= scale

    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)

    ax.set_aspect("equal")

    ax.xaxis.set_major_locator(MaxNLocator(6))
    ax.yaxis.set_major_locator(MaxNLocator(6))

    ax.set_xlabel("x [km]")
    ax.set_ylabel("y [km]")

    ax.legend()
    plt.show()


def animate_orbit(sat, step, dt):

    trajectory = []

    fig, ax = plt.subplots(figsize=(8, 8))

    earth = plt.Circle(
        (0, 0),
        EARTH_RADIUS * KM,
        color='blue',
        alpha=0.5,
        label="Earth"
    )
    ax.add_patch(earth)

    line, = ax.plot([], [], label="Trajectory")
    point = ax.scatter([], [], label="Satellite")

    ax.set_aspect("equal")
    ax.xaxis.set_major_locator(MaxNLocator(6))
    ax.yaxis.set_major_locator(MaxNLocator(6))

    ax.set_xlabel("x [km]")
    ax.set_ylabel("y [km]")

    ax.legend()

    start_x, start_y = sat.position
    start_angle = np.arctan2(start_y, start_x)

    iterations = 0
    iterations_breakout = 0
    running = True

    base = np.linalg.norm(sat.position) * KM
    base = base if base > 0 else 1
    ax.set_xlim(-base * 2, base * 2)
    ax.set_ylim(-base * 2, base * 2)

    ani = None

    def update(_):

        nonlocal iterations, iterations_breakout, running, ani

        if not running:
            return line, point

        iterations += 1

        step(sat, dt)

        trajectory.append(sat.position.copy())

        traj = np.array(trajectory) * KM

        line.set_data(traj[:, 0], traj[:, 1])
        point.set_offsets(traj[-1])

        limit = np.max(np.linalg.norm(traj, axis=1))
        scale = 1 + 1 / (1 + limit / 1e7)
        limit *= scale

        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)

        if np.allclose(sat.position, [start_x, start_y], atol=10000) and iterations > 1: 
            print("Orbit completed after " + str(iterations) + " iterations.") 
            print("Final position: " + str(sat.position[0])) 
            
            running = False 
        elif np.linalg.norm(sat.position) <= EARTH_RADIUS: 
            print("Satellite has crashed into Earth after " + str(iterations) + " iterations.") 
            print("Final position: " + str(sat.position[0])) 
            
            running = False 
        elif np.abs(round(start_angle, 10) - round(atan2(sat.position[1], sat.position[0]), 10)) == 0 and iterations > 1: 
            iterations_breakout = iterations 

        if iterations == 2 * iterations_breakout: 
            print("Satellite has escaped Earth's gravity after " + str(iterations) + " iterations.") 
            
            running = False

        return line, point

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=200000,
        interval=10,
        blit=False
    )

    plt.show()