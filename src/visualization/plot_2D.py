import matplotlib.pyplot as plt
import numpy as np
from numpy import atan2
from matplotlib.ticker import MaxNLocator
from matplotlib import animation
from src.simulation.satellite import Satellite

from src.physics.constants import EARTH_RADIUS, KM
from skimage.measure import EllipseModel


def animate_orbit(sat, step, dt):

    max_points = 50
    trajectory = []
    angle = []
    distance = []
    velocity = []
    orbit_progress = 0

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

    info_label = ax.text(
        0.05,
        0.95,
        "",
        fontsize=12,
        transform=ax.transAxes,
        verticalalignment="top"
    )

    start_x, start_y = sat.position

    iterations = 0

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)

    # -----------------------------
    # PHYSICS SIMULATION PHASE
    # -----------------------------
    while True:

        iterations += 1

        step(sat, dt)

        sat.update_distance()

        trajectory.append(sat.position.copy() * KM)
        distance.append(sat.distance_from_earth * KM)
        velocity.append(sat.velocity.copy() * KM * 3600)
        if np.allclose(sat.position, [start_x, start_y], atol=10000) and iterations > 1:
            print("Orbit completed after " + str(iterations) + " iterations.")
            break

        elif np.linalg.norm(sat.position) <= EARTH_RADIUS:
            print("Satellite has crashed into Earth after " + str(iterations) + " iterations.")
            break

        if iterations > 200000:
            print("Max iterations reached.")
            break
    
    orbit_progress = np.linspace(0, 1, len(trajectory))
    trajectory = np.array(trajectory)
    
    distance = np.array(distance)
    velocity = np.array(velocity)
    
    line.set_data(trajectory[:, 0], trajectory[:, 1])
    # -----------------------------
    # ELLIPSE FITTING PHASE (UPDATED API FIX)
    # -----------------------------
    model = EllipseModel.from_estimate(trajectory)
    

    xc, yc = model.center
    a, b = model.axis_lengths
    theta = model.theta

    for i in range(len(trajectory)):
        angle.append(Satellite.update_angle(trajectory[i][0], trajectory[i][1], xc, yc))
    angle = np.array(angle)

    # -----------------------------
    # AUTO CENTER + ZOOM FIX
    # -----------------------------
    margin = 1.3 * max(a, b)

    ax.set_xlim(xc - margin, xc + margin)
    ax.set_ylim(yc - margin, yc + margin)

    # -----------------------------
    # ANIMATION PHASE (REAL PHYSICS)
    # -----------------------------

    finished = False

    animation_iterations = 0
    animation_speed_multiplier = 15

    def update(_):

        nonlocal finished, animation_iterations

        if finished:
            return line, point, info_label

        if animation_iterations >= len(trajectory):
            finished = True
            return line, point, info_label

        

        x, y = trajectory[animation_iterations]

        point.set_offsets([[x, y]])

        info_label.set_text(
            f"Speed: {np.linalg.norm(velocity[animation_iterations]):.0f} km/h\n"
            # f"Center: ({xc:.0f}, {yc:.0f}) km\n"
            f"Orbit height: {distance[animation_iterations]:.0f}km\n"
            f"Angle: {angle[animation_iterations]:.1f}°\n"
            f"Orbit progress: {orbit_progress[animation_iterations]*100:.1f}%"
        )

        if animation_iterations == len(trajectory) - 1:
            # If we just rendered the final frame, increment by 1 to trigger the finish condition next round
            animation_iterations += 1
        else:
            # Jump forward by the speed multiplier, but cap it at the very last index
            animation_iterations = min(animation_iterations + animation_speed_multiplier, len(trajectory) - 1)

        return line, point, info_label

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=200000,
        interval=1,
        blit=True,
    )

    plt.show()