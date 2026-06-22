import matplotlib.pyplot as plt
import numpy as np
from numpy import atan2
from matplotlib.ticker import MaxNLocator
from matplotlib import animation
from matplotlib.widgets import Button  
import matplotlib.gridspec as gridspec

from src.simulation.satellite import Satellite
from src.physics.constants import EARTH_RADIUS, KM, G, EARTH_MASS

def animate_orbit(sat, step, dt):
    
    trajectory = []
    angle = []
    distance = []
    velocity = []
    
    # --- GridSpec Layout ---
    fig = plt.figure(figsize=(14, 8))
    gs = gridspec.GridSpec(2, 2, width_ratios=[2, 1])
    
    ax = fig.add_subplot(gs[:, 0]) # Main orbit plot
    ax_dist = fig.add_subplot(gs[0, 1]) # Altitude plot
    ax_vel = fig.add_subplot(gs[1, 1]) # Velocity plot

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


    ax.set_aspect("equal") 
    ax.xaxis.set_major_locator(MaxNLocator(6)) 
    ax.yaxis.set_major_locator(MaxNLocator(6))

    ax.set_xlabel("x [km]")
    ax.set_ylabel("y [km]")
    
    info_label = ax.text(
        0.05,
        0.95,
        "",
        fontsize=12,
        transform=ax.transAxes, 
        verticalalignment="top",
        fontname='monospace'
    )

    start_x, start_y = sat.position
    iterations = 0

    ax.set_xlim(-1, 1) 
    ax.set_ylim(-1, 1)

    # -----------------------------
    # 1. PHYSICS SIMULATION 
    # -----------------------------

    print("Simulating orbit... Please wait.")
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
    
    # -----------------------------
    # 2. PRE-CALCULATE ALL TELEMETRY (The Speed Hack)
    # -----------------------------
    print("Calculating telemetry arrays...")
    
    trajectory = np.array(trajectory)
    distance = np.array(distance)
    velocity = np.array(velocity)
    
    # Basic Time and Speed
    time_data = np.arange(len(trajectory)) * dt
    v_ms_data = np.linalg.norm(velocity, axis=1) # Speed in m/s
    speed_data = v_ms_data / 1000                # Speed in km/s
    speed_kmh_data = speed_data * 3600           # Speed in km/h
    
    # Radius in meters
    r_meters_data = distance * 1000 + EARTH_RADIUS
    
    # Specific Energy
    energy_j_kg_data = (v_ms_data**2 / 2) - ((G * EARTH_MASS) / r_meters_data)
    energy_mj_kg_data = energy_j_kg_data / 1_000_000
    
    # Specific Angular Momentum (np.cross on arrays returns the cross product for every step at once)
    momentum_data = np.abs(np.cross(trajectory * 1000, velocity))
    
    # Gravitational Acceleration Vector
    g_mag_data = (G * EARTH_MASS) / (r_meters_data**2)
    # np.newaxis to divide the 2D trajectory array by the 1D radius array
    unit_vector_data = (-trajectory * 1000) / r_meters_data[:, np.newaxis] 
    grav_accel_data = g_mag_data[:, np.newaxis] * unit_vector_data
    grav_accel_norm_data = np.linalg.norm(grav_accel_data, axis=1)

    # Setup Altitude Plot
    ax_dist.set_title("Altitude over Time")
    ax_dist.set_ylabel("Altitude [km]")
    ax_dist.set_xlim(0, time_data[-1])
    ax_dist.set_ylim(min(distance) * 0.9, max(distance) * 1.1)
    line_dist, = ax_dist.plot([], [], color='green')

    # Setup Velocity Plot
    ax_vel.set_title("Velocity over Time")
    ax_vel.set_ylabel("Velocity [km/s]")
    ax_vel.set_xlabel("Time [s]")
    ax_vel.set_xlim(0, time_data[-1])
    ax_vel.set_ylim(min(speed_data) * 0.9, max(speed_data) * 1.1)
    line_vel, = ax_vel.plot([], [], color='purple')

    line.set_data(trajectory[:, 0], trajectory[:, 1])

    # -----------------------------
    # 3. ORBITAL MECHANICS  
    # -----------------------------

    index_peri = np.argmin(distance) 
    index_apo = np.argmax(distance)

    vec_peri = trajectory[index_peri] 
    perigee = np.linalg.norm(vec_peri) - EARTH_RADIUS * KM
    vec_apo = trajectory[index_apo]
    apogee = np.linalg.norm(vec_apo) - EARTH_RADIUS * KM

    major_axis_vec = vec_apo - vec_peri 
    a = np.linalg.norm(major_axis_vec) / 2.0 

    center = vec_peri + major_axis_vec / 2.0
    xc, yc = center[0], center[1]

    c = np.linalg.norm(center) 
    b = np.sqrt(max(0, a**2 - c**2)) 

    theta = np.arctan2(vec_peri[1], vec_peri[0]) 

    e = c/a 

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
    # 4. AUTO CENTER + ZOOM FIX
    # -----------------------------

    margin = 1.3 * max(a, b)
    ax.set_xlim(xc - margin, xc + margin)
    ax.set_ylim(yc - margin, yc + margin)
    ax.legend()

    # -----------------------------
    # 5. ANIMATION PHASE (READ AND DRAW ONLY)
    # -----------------------------

    finished = False
    animation_iterations = 0
    
    # Tweak this multiplier higher if you still want the satellite to fly faster!
    animation_speed_multiplier = 10

    def update(_):
        nonlocal finished, animation_iterations

        if finished:
            return line, point, info_label, g_vector, line_dist, line_vel

        if animation_iterations >= len(trajectory):
            finished = True
            return line, point, info_label, g_vector, line_dist, line_vel

        # Fetch position
        x, y = trajectory[animation_iterations]
        point.set_offsets([[x, y]])

        # Fetch gravity vector
        gx, gy = grav_accel_data[animation_iterations]
        g_vector.set_offsets([[x, y]]) 
        g_vector.set_UVC(gx, gy) 

        # Fetch data for label
        info_label.set_text(
            f"Speed:                {speed_kmh_data[animation_iterations]:,.0f} km/h\n"
            f"Orbit height:         {(distance[animation_iterations]):,.0f} km\n"
            f"Progress (Arc lenght):{angle[animation_iterations]*360:.2f}°\n"
            f"Spec. Energy:         {energy_mj_kg_data[animation_iterations]:.2f} MJ/kg\n"    
            f"Spec. Ang. Momentum:  {momentum_data[animation_iterations]:.2e} m^2/s\n"        
            f"Gravitational acc.:   {grav_accel_norm_data[animation_iterations]:.2f} m/s^2\n"
            f"Obrit Period:         {(orbit_period / (3600)):.2f} h\n"
            f"Eccentricity:         {e:.2f}\n"
            f"Apogee, Perigee:      {apogee:.2f}km, {perigee:.2f}km"
        )       

        # Update telemetry lines (using [::10] decimation to skip points and draw faster)
        line_dist.set_data(time_data[:animation_iterations:10], distance[:animation_iterations:10])
        line_vel.set_data(time_data[:animation_iterations:10], speed_data[:animation_iterations:10])

        if animation_iterations == len(trajectory) - 1:
            animation_iterations += 1
        else:
            animation_iterations = min(animation_iterations + animation_speed_multiplier, len(trajectory) - 1)

        return line, point, info_label, g_vector, line_dist, line_vel

    print("Launching animation...")
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=200000,
        interval=1,
        blit=True,
    )

    def restart_animation(event):
        print("Button pressed")
        ani.frame_seq = ani.new_frame_seq()  
        ani.event_source.start()

    plt.subplots_adjust(bottom=0.15)
    button_ax = plt.axes([0.45, 0.05, 0.1, 0.05]) 
    restart_button = Button(button_ax, 'Restart')
    restart_button.on_clicked(restart_animation)

    plt.show()