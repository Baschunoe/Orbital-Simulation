import sys
import numpy as np
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QPixmap, QBrush, QColor

from src.physics.constants import EARTH_RADIUS, KM, G, EARTH_MASS
from src.visualization.plot_2D import orbital_data_2D
from src.visualization.helpers import load_arrays, telemetry
from src.visualization.orbital_mechanics import orbital_mechanics

def animate_orbit(sat, step, dt):

    # -----------------------------
    # DATHER 3D DATA 
    # -----------------------------
    
    (trajectory3D, distance, velocity) = load_arrays(sat, step, dt)

    # -----------------------------
    # GATHER TELEMETRY DATA
    # -----------------------------

    (perigee, apogee, a, b, xc, yc, theta, e, angle, orbit_period) = orbital_mechanics(trajectory3D, distance)

    # -----------------------------
    # GATHER 2D DATA
    # -----------------------------
        
    trajectory = orbital_data_2D(trajectory3D, e)

    # -----------------------------
    # GATHER TELEMETRY DATA
    # -----------------------------

    (time_data, speed_data, speed_kmh_data, energy_mj_kg_data, momentum_data, grav_accel_data, grav_accel_norm_data) = telemetry(trajectory3D, distance, velocity, dt)

    # -----------------------------
    # PYQTGRAPH UI SETUP 
    # -----------------------------

    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    # --- Modern UI Styling (QSS) ---
    app.setStyleSheet("""
        QMainWindow {
            background-color: #0B0F19; /* Deep Space Slate */
        }
        QPushButton {
            background-color: #1E293B;
            color: #E2E8F0;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 12px;
            font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 1px;
        }
        QPushButton:hover {
            background-color: #2DD4BF; /* Teal Glow */
            color: #0B0F19;
            border: 1px solid #2DD4BF;
        }
        QPushButton:pressed {
            background-color: #14B8A6;
        }
    """)

    # Global pyqtgraph settings for a soulful look
    pg.setConfigOptions(antialias=True)
    pg.setConfigOption('background', '#0B0F19')
    pg.setConfigOption('foreground', '#8A9AB2')
    pg.setConfigOptions(useOpenGL=True)

    win = QtWidgets.QMainWindow()
    win.setWindowTitle("Orbital Dynamics Visualization")
    win.resize(1400, 850)
    
    central_widget = QtWidgets.QWidget()
    win.setCentralWidget(central_widget)
    main_layout = QtWidgets.QVBoxLayout(central_widget)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(15)
    
    glw = pg.GraphicsLayoutWidget()
    main_layout.addWidget(glw)
    
    # Configure Axes fonts
    axis_font = QtGui.QFont("Segoe UI", 10)
    
    ax = glw.addPlot(row=0, col=0, rowspan=2, title="Trajectory Overview")
    ax_dist = glw.addPlot(row=0, col=1, title="Altitude Over Time")
    ax_vel = glw.addPlot(row=1, col=1, title="Velocity Over Time")

    # Apply modern styling to titles
    for plot in [ax, ax_dist, ax_vel]:
        title_text = plot.titleLabel.text
        plot.setTitle(f'<span style="font-family: Segoe UI; font-size: 14pt; color: #E2E8F0;">{title_text}</span>')

    # --- Orbit Plot Configuration ---
    ax.setAspectLocked(True)
    ax.setLabel('bottom', "x-axis [km]")
    ax.setLabel('left', "y-axis [km]")
    ax.getAxis('bottom').setTickFont(axis_font)
    ax.getAxis('left').setTickFont(axis_font)
    ax.showGrid(x=True, y=True, alpha=0.1) # Very subtle grid
    
    margin = 1.3 * max(a, b)
    ax.setXRange(xc - margin, xc + margin)
    ax.setYRange(yc - margin, yc + margin)

    # Draw Earth (Modern wireframe/blueprint style)
    earth_radius_km = EARTH_RADIUS * KM
    earth = QtWidgets.QGraphicsEllipseItem(-earth_radius_km, -earth_radius_km, earth_radius_km * 2, earth_radius_km * 2)
    earth.setBrush(pg.mkBrush(QColor(30, 41, 59, 200))) # Dark transparent slate
    earth.setPen(pg.mkPen(color='#3B82F6', width=2, style=QtCore.Qt.PenStyle.DashLine)) # Blue dashed edge
    ax.addItem(earth)

    # Draw full trajectory path (Smooth dark blue)
    ax.plot(trajectory[:, 0], trajectory[:, 1], pen=pg.mkPen(color=(59, 130, 246, 150), width=1.5))

    # Draw Center, a, and b axes (Subtle indicators)
    ax.plot([xc], [yc], pen=None, symbol='+', symbolPen='#64748B', symbolSize=12)
    ax.plot([xc, xc + a*np.cos(theta)], [yc, yc + a*np.sin(theta)], pen=pg.mkPen('#10B981', style=QtCore.Qt.PenStyle.DotLine, width=1))
    ax.plot([xc, xc + b*np.cos(theta + np.pi/2)], [yc, yc + b*np.sin(theta + np.pi/2)], pen=pg.mkPen('#F59E0B', style=QtCore.Qt.PenStyle.DotLine, width=1))

    # Animated elements
    sat_point = ax.plot([], [], pen=None, symbol='o', symbolBrush='#2DD4BF', symbolSize=10, symbolPen=pg.mkPen('#0B0F19', width=2))
    g_vector = ax.plot([], [], pen=pg.mkPen(color='#EF4444', width=2)) # Red gravity vector
    
    # Telemetry Text Label (Modern Monospace)
    info_label = pg.TextItem("", color='#E2E8F0', anchor=(0, 0))
    info_label.setFont(QtGui.QFont("Consolas", 11))
    ax.addItem(info_label)
    info_label.setPos(xc - margin*0.95, yc + margin*0.95)

    # --- Altitude Plot Setup (Emerald Theme) ---
    ax_dist.setLabel('left', "Altitude [km]")
    ax_dist.setLabel('bottom', "Time [s]")
    ax_dist.getAxis('bottom').setTickFont(axis_font)
    ax_dist.getAxis('left').setTickFont(axis_font)
    ax_dist.setXRange(0, time_data[-1])
    ax_dist.setYRange(min(distance) * 0.9, max(distance) * 1.1)
    ax_dist.disableAutoRange()
    ax_dist.showGrid(x=True, y=True, alpha=0.1)
    ax_dist.getAxis('left').setWidth(70)
    
    # Beautiful filled curve
    curve_dist = ax_dist.plot(time_data, distance, pen=pg.mkPen(color='#10B981', width=2))
    curve_dist.setFillLevel(min(distance) * 0.8)
    curve_dist.setBrush(pg.mkBrush(QColor(16, 185, 129, 30))) # Transparent emerald fill
    
    dist_point = ax_dist.plot([], [], pen=None, symbol='o', symbolBrush='#10B981', symbolSize=8, symbolPen=pg.mkPen('#0B0F19', width=1))

    # --- Velocity Plot Setup (Amber Theme) ---
    ax_vel.setLabel('left', "Velocity [km/s]")
    ax_vel.setLabel('bottom', "Time [s]")
    ax_vel.getAxis('bottom').setTickFont(axis_font)
    ax_vel.getAxis('left').setTickFont(axis_font)
    ax_vel.setXRange(0, time_data[-1])
    ax_vel.setYRange(min(speed_data) * 0.9, max(speed_data) * 1.1)
    ax_vel.disableAutoRange()
    ax_vel.showGrid(x=True, y=True, alpha=0.1)
    ax_vel.getAxis('left').setWidth(70)
    
    # Beautiful filled curve
    curve_vel = ax_vel.plot(time_data, speed_data, pen=pg.mkPen(color='#F59E0B', width=2))
    curve_vel.setFillLevel(min(speed_data) * 0.8)
    curve_vel.setBrush(pg.mkBrush(QColor(245, 158, 11, 30))) # Transparent amber fill
    
    vel_point = ax_vel.plot([], [], pen=None, symbol='o', symbolBrush='#F59E0B', symbolSize=8, symbolPen=pg.mkPen('#0B0F19', width=1))

    # Restart Button Setup
    button_layout = QtWidgets.QHBoxLayout()
    restart_button = QtWidgets.QPushButton("RESTART SIMULATION")
    restart_button.setFixedWidth(250)
    restart_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
    button_layout.addStretch()
    button_layout.addWidget(restart_button)
    button_layout.addStretch()
    main_layout.addLayout(button_layout)

    # -----------------------------
    # ANIMATION  
    # -----------------------------

    finished = False
    animation_iterations = 0
    ui_iterations = 0
    animation_speed_multiplier = max(1, len(trajectory) // 1000)

    def update():
        nonlocal finished, animation_iterations, ui_iterations

        if finished:
            return

        if animation_iterations >= len(trajectory):
            animation_iterations = 0
            return

        # Fetch positions
        x, y = trajectory[animation_iterations]
        sat_point.setData([x], [y])

        current_time = time_data[animation_iterations]
        dist_point.setData([current_time], [distance[animation_iterations]])
        vel_point.setData([current_time], [speed_data[animation_iterations]])

        # Fetch gravity vector
        gx, gy = grav_accel_data[animation_iterations]
        quiver_scale = a * 0.05 
        g_vector.setData([x, x + gx * quiver_scale], [y, y + gy * quiver_scale])

        ui_iterations += 1
        if ui_iterations % 2 == 0:
            text_str = (
                f"Speed                : {speed_kmh_data[animation_iterations]:,.0f} km/h\n"
                f"Altitude             : {distance[animation_iterations]:,.0f} km\n"
                f"Arc Progress         : {angle[animation_iterations]*360:.1f}°\n"
                f"Spec. Energy         : {energy_mj_kg_data[animation_iterations]:.2f} MJ/kg\n"    
                f"Ang. Momentum        : {momentum_data[animation_iterations]:.2e} m²/s\n"        
                f"Gravitational Accel. : {grav_accel_norm_data[animation_iterations]:.2f} m/s²\n"
                f"Orbit Period         : {(orbit_period / 3600):.2f} h\n"
                f"Eccentricity         : {e:.3f}\n"
                f"Apogee / Perigee     : {apogee:.0f} km / {perigee:.0f} km"
            )
            info_label.setText(text_str)

        if animation_iterations == len(trajectory) - 1:
            animation_iterations += 1
        else:
            animation_iterations = min(animation_iterations + animation_speed_multiplier, len(trajectory) - 1)

    def restart_animation():
        print("Restarting animation...")
        nonlocal finished, animation_iterations
        finished = False
        animation_iterations = 0

    restart_button.clicked.connect(restart_animation)

    # Start QTimer for the animation loop
    print("Launching animation UI...")
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(16) # ~60fps target

    win.show()
    sys.exit(app.exec())

    return sat_point, dist_point, vel_point, g_vector, info_label, restart_button, win, app