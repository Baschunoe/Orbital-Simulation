import matplotlib.pyplot as plt
import numpy as np
from numpy import atan2
from matplotlib.ticker import MaxNLocator
from matplotlib import animation
from matplotlib.widgets import Button  

from src.simulation.satellite import Satellite
from src.physics.constants import EARTH_RADIUS, KM, G, EARTH_MASS

def animate_orbit(sat, step, dt):
    
    trajectory = []
    angle = []
    distance = []
    velocity = []
    
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
    g_vector = ax.quiver([], [], [], [], color='red', scale=40, width=0.005, label="Gravity (g)")


    ax.set_aspect("equal") # Set x and y axis to be equal
    ax.xaxis.set_major_locator(MaxNLocator(6)) # Max number of sections per axis
    ax.yaxis.set_major_locator(MaxNLocator(6))

    ax.set_xlabel("x [km]")
    ax.set_ylabel("y [km]")
    

    info_label = ax.text(
        0.05,
        0.95,
        "",
        fontsize=12,
        transform=ax.transAxes, # Fixing info_label to coordinate system
        verticalalignment="top",
        fontname='monospace'
    )

    start_x, start_y = sat.position
    iterations = 0

    ax.set_xlim(-1, 1) 
    ax.set_ylim(-1, 1)

   

    # -----------------------------
    # PHYSICS SIMULATION 
    # -----------------------------

    while True:

        iterations += 1
        step(sat, dt) # Calculate new position and velocity after one step
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
    
    trajectory = np.array(trajectory)
    distance = np.array(distance)
    velocity = np.array(velocity)
    
    line.set_data(trajectory[:, 0], trajectory[:, 1])


    
    # -----------------------------
    # ORBITAL MECHANICS  
    # -----------------------------

    index_peri = np.argmin(distance) # Indexes of the extreme values
    index_apo = np.argmax(distance)

    vec_peri = trajectory[index_peri] # Vector to extreme values via indexes
    perigee = np.linalg.norm(vec_peri) - EARTH_RADIUS * KM
    vec_apo = trajectory[index_apo]
    apogee = np.linalg.norm(vec_apo) - EARTH_RADIUS * KM

    major_axis_vec = vec_apo - vec_peri 
    a = np.linalg.norm(major_axis_vec) / 2.0 # Lenght of semi-major axis

    center = vec_peri + major_axis_vec / 2.0
    xc, yc = center[0], center[1]

    c = np.linalg.norm(center) # Distance focal point (Earth) and center 
    b = np.sqrt(max(0, a**2 - c**2)) # Semi-minor axis

    theta = np.arctan2(vec_peri[1], vec_peri[0]) # Tilt relative to X-Axis

    e = c/a # Eccentricity  

    print(f"Calculated True Orbital parameters:\n Center: ({xc:.2f}, {yc:.2f}) km\n Semi-major axis: {a:.2f} km\n Semi-minor axis: {b:.2f} km\n Rotation angle: {np.degrees(theta):.2f}°")

    ax.scatter(xc, yc, color='black', alpha=0.5, marker='x', label="Orbit Center")
    
    ax.plot([xc, xc + a*np.cos(theta)], [yc, yc + a*np.sin(theta)], linestyle=':', color='green', alpha=0.5, label="a")
    ax.plot([xc, xc + b*np.cos(theta + np.pi/2)], [yc, yc + b*np.sin(theta + np.pi/2)], linestyle=':', color='red', alpha=0.5, label="b")

    diffs = np.diff(trajectory, axis=0)
    step_lengths = np.linalg.norm(diffs, axis=1)
    s = np.insert(np.cumsum(step_lengths), 0, 0)
    angle = s / s[-1]

    orbit_period = 2 * np.pi * np.sqrt(((a * 1000)**3) / (G * EARTH_MASS))



    # -----------------------------
    # AUTO CENTER + ZOOM FIX
    # -----------------------------

    margin = 1.3 * max(a, b)

    ax.set_xlim(xc - margin, xc + margin)
    ax.set_ylim(yc - margin, yc + margin)

    ax.legend()



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

        v_ms = np.linalg.norm(velocity[animation_iterations])
        speed_kmh = (v_ms / 1000) * 3600
        
        r_meters = distance[animation_iterations] * 1000 + EARTH_RADIUS
        
        # Specific Energy
        energy_j_kg = (v_ms**2 / 2) - ((G * EARTH_MASS) / r_meters)
        energy_mj_kg = energy_j_kg / 1_000_000

        # Specific angular Momentum
        specific_angular_momentum = float(np.abs(np.cross(trajectory[animation_iterations] * 1000, velocity[animation_iterations])))

        # Vector gravitional acceleration
        g_mag = (G * EARTH_MASS) / (r_meters**2)
        unit_vector = (-trajectory[animation_iterations] * 1000) / r_meters
        gravitational_acceleration = g_mag * unit_vector

        g_vector.set_offsets([[x, y]]) # Set base of the arrow to satellite position
        g_vector.set_UVC(gravitational_acceleration[0], gravitational_acceleration[1]) 

        info_label.set_text(
            f"Speed:                {speed_kmh:,.0f} km/h\n"
            f"Orbit height:         {(distance[animation_iterations]):,.0f} km\n"
            f"Progress (Arc lenght):{angle[animation_iterations]*360:.2f}°\n"
            f"Spec. Energy:         {energy_mj_kg:.2f} MJ/kg\n"    
            f"Spec. Ang. Momentum:  {specific_angular_momentum:.2e} m^2/s\n"        
            f"Gravitational acc.:   {np.linalg.norm(gravitational_acceleration):.2f} m/s^2\n"
            f"Obrit Period:         {(orbit_period / (3600)):.2f} h\n"
            f"Eccentricity:         {e:.2f}\n"
            f"Apogee, Perigee:      {apogee:.2f}km, {perigee:.2f}km"
        )       

        if animation_iterations == len(trajectory) - 1:
            animation_iterations += 1
        else:
            animation_iterations = min(animation_iterations + animation_speed_multiplier, len(trajectory) - 1)

        return line, point, info_label, g_vector

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=200000,
        interval=1,
        blit=True,
    )

    def restart_animation(event):
        print("Button pressed")
        ani.frame_seq = ani.new_frame_seq()  # Reset the internal frame sequence generator
        ani.event_source.start()

    button_ax = plt.axes([0.45, 0.05, 0.12, 0.05]) 
    restart_button = Button(button_ax, 'Restart')
    restart_button.on_clicked(restart_animation)

    plt.show()