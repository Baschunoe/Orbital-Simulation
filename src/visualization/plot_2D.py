import matplotlib.pyplot as plt
import numpy as np
from numpy import atan2
from matplotlib.ticker import MaxNLocator
from matplotlib import animation
from matplotlib.patches import Ellipse  

from src.simulation.satellite import Satellite
from src.physics.constants import EARTH_RADIUS, KM, G, EARTH_MASS

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
        verticalalignment="top",
        family='monospace' # Added monospace for a cleaner telemetry look
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
        velocity.append(sat.velocity.copy())
        
        if np.allclose(sat.position, [start_x, start_y], atol=10000) and iterations > 1:
            print("Orbit completed after " + str(iterations) + " iterations.")
            break

        elif np.linalg.norm(sat.position) <= EARTH_RADIUS:
            print("Satellite has crashed into Earth after " + str(iterations) + " iterations.")
            break

        if iterations > 10000000:
            print("Max iterations reached.")
            break
    
    orbit_progress = np.linspace(0, 1, len(trajectory))
    trajectory = np.array(trajectory)
    distance = np.array(distance)
    velocity = np.array(velocity)
    
    line.set_data(trajectory[:, 0], trajectory[:, 1])
    
    # -----------------------------
    # ORBITAL MECHANICS PHASE 
    # -----------------------------
    radii = np.linalg.norm(trajectory, axis=1)
    idx_peri = np.argmin(radii)
    idx_apo = np.argmax(radii)

    r_peri = trajectory[idx_peri]
    r_apo = trajectory[idx_apo]

    major_axis_vec = r_apo - r_peri
    a = np.linalg.norm(major_axis_vec) / 2.0

    center = r_peri + major_axis_vec / 2.0
    xc, yc = center[0], center[1]

    c = np.linalg.norm(center)    
    b = np.sqrt(max(0, a**2 - c**2))

    theta = np.arctan2(r_peri[1], r_peri[0])

    print(f"Calculated True Orbital parameters:\n Center: ({xc:.2f}, {yc:.2f}) km\n Semi-major axis: {a:.2f} km\n Semi-minor axis: {b:.2f} km\n Rotation angle: {np.degrees(theta):.2f}°")

    orbit_ellipse = Ellipse(
        xy=(xc, yc),
        width=2*a,
        height=2*b,
        angle=np.degrees(theta),
        edgecolor='black',
        facecolor='none',
        linestyle='--',
        alpha=0.3,
        label="True Orbit (Physics)"
    )
    ax.add_patch(orbit_ellipse)
    ax.scatter(xc, yc, color='black', alpha=0.5, marker='x', label="Orbit Center")
    
    ax.plot([xc, xc + a*np.cos(theta)], [yc, yc + a*np.sin(theta)], linestyle=':', color='black', alpha=0.2)
    ax.plot([xc, xc + b*np.cos(theta + np.pi/2)], [yc, yc + b*np.sin(theta + np.pi/2)], linestyle=':', color='black', alpha=0.2)

    diffs = np.diff(trajectory, axis=0)
    step_lengths = np.linalg.norm(diffs, axis=1)
    s = np.insert(np.cumsum(step_lengths), 0, 0)
    angle = s / s[-1]

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

        # 1. Update positions
        x, y = trajectory[animation_iterations]
        point.set_offsets([[x, y]])

        # 2. Extract cleanly formatted variables for UI
        # Assuming your velocity array stores km/s, multiply by 1000 to get standard m/s
        v_ms = np.linalg.norm(velocity[animation_iterations])
        speed_kmh = (v_ms / 1000) * 3600
        
        # Assuming your EARTH_RADIUS is already in meters based on previous chats
        r_meters = distance[animation_iterations] + EARTH_RADIUS
        
        # 3. Calculate Energy (now in standard Joules/kg)
        energy_j_kg = (v_ms**2 / 2) - ((G * EARTH_MASS) / r_meters)
        energy_mj_kg = energy_j_kg / 1_000_000

        specific_angular_momentum = float(np.abs(np.cross(trajectory[animation_iterations] * 1000, velocity[animation_iterations])))
        # 4. Clean UI Rendering
        info_label.set_text(
            f"Speed:               {speed_kmh:,.0f} km/h\n"
            f"Orbit height:        {(distance[animation_iterations] / 1000):,.0f} km\n"
            f"Angle:               {angle[animation_iterations]*360:.2f}°\n"
            f"Orbit progress:      {orbit_progress[animation_iterations]*100:.2f}%\n"
            f"Spec. Energy:        {energy_mj_kg:.2f} MJ/kg\n"    
            f"Spec. Ang. Momentum: {specific_angular_momentum:.2e} m^2/s"        
        )       

        if animation_iterations == len(trajectory) - 1:
            animation_iterations += 1
        else:
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