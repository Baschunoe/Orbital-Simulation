import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

def plot_orbit(trajectory):

    trajectory = np.array(trajectory)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        trajectory[:, 0],
        trajectory[:, 1],
        label="Trajectory"
    )

    ax.scatter(
        0,
        0,
        s=200,
        label="Earth"
    )

    ax.scatter(
        trajectory[-1, 0],
        trajectory[-1, 1],
        label="Satellite"
    )

    ax.set_aspect("equal")

    ax.xaxis.set_major_locator(MaxNLocator(8))
    ax.yaxis.set_major_locator(MaxNLocator(8))

    ax.ticklabel_format(style='plain')

    # Disable scientific notation
    ax.ticklabel_format(style='plain', axis='both')

    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")

    ax.legend()

    plt.show()