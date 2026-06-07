import matplotlib.pyplot as plt
import numpy as np
from numpy import atan2
from matplotlib.ticker import MaxNLocator
from matplotlib import animation
import copy 

from src.physics.constants import EARTH_RADIUS, KM
from skimage.measure import EllipseModel


# def plot_orbit(trajectory):

#     trajectory = np.array(trajectory) * KM

#     ax = plt.subplots(figsize=(8, 8))

#     ax.plot(trajectory[:, 0], trajectory[:, 1], label="Trajectory")

#     earth = plt.Circle(
#         (0, 0),
#         EARTH_RADIUS * KM,
#         color='blue',
#         alpha=0.5,
#         label="Earth"
#     )
#     ax.add_patch(earth)

#     ax.scatter(trajectory[-1, 0], trajectory[-1, 1], label="Satellite")

#     limit = np.max(np.linalg.norm(trajectory, axis=1))
#     scale = 1 + 1 / (1 + limit / 1e7)
#     limit *= scale

#     ax.set_xlim(-limit, limit)
#     ax.set_ylim(-limit, limit)

#     ax.set_aspect("equal")

#     ax.xaxis.set_major_locator(MaxNLocator(6))
#     ax.yaxis.set_major_locator(MaxNLocator(6))

#     ax.set_xlabel("x [km]")
#     ax.set_ylabel("y [km]")

#     ax.legend()
#     plt.show()


def animate_orbit(sat, step, dt):

    max_points = 50
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

        trajectory.append(sat.position.copy() * KM)

        if np.allclose(sat.position, [start_x, start_y], atol=10000) and iterations > 1:
            print("Orbit completed after " + str(iterations) + " iterations.")
            break

        elif np.linalg.norm(sat.position) <= EARTH_RADIUS:
            print("Satellite has crashed into Earth after " + str(iterations) + " iterations.")
            break

        if iterations > 200000:
            print("Max iterations reached.")
            break

    trajectory = np.array(trajectory)

    # -----------------------------
    # ELLIPSE FITTING PHASE (UPDATED API FIX)
    # -----------------------------
    model = EllipseModel.from_estimate(trajectory)

    xc, yc = model.center
    a, b = model.axis_lengths
    theta = model.theta

    # -----------------------------
    # AUTO CENTER + ZOOM FIX
    # -----------------------------
    margin = 1.3 * max(a, b)

    ax.set_xlim(xc - margin, xc + margin)
    ax.set_ylim(yc - margin, yc + margin)

    # -----------------------------
    # ANIMATION PHASE (REAL PHYSICS)
    # -----------------------------

    crashed = False
    finished = False

    sat_animation = copy.deepcopy(sat)

    def update(_):

        nonlocal crashed, finished, sat_animation

        if finished:
            return line, point, info_label

        vis_speedup = 10

        for _ in range(vis_speedup):

            step(sat_animation, dt)

            if np.linalg.norm(sat_animation.position) <= EARTH_RADIUS:
                print("Satellite has crashed into Earth during animation.")
                crashed = True
                finished = True
                

        # trajectory stays from pre-sim (correct)
        line.set_data(trajectory[:, 0], trajectory[:, 1])

        # live satellite from animation copy
        x, y = sat_animation.position * KM
        point.set_offsets([x, y])

        info_label.set_text(
            f"Speed: {np.linalg.norm(sat_animation.velocity):.0f} m/s\n"
            f"Center: ({xc:.0f}, {yc:.0f}) km"
        )

        return line, point, info_label

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=200000,
        interval=10,
        blit=False
    )

    plt.show()