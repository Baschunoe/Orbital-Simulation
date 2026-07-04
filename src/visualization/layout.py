import sys
import os
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QPixmap, QBrush, QColor

from src.physics.constants import EARTH_RADIUS, KM, G, EARTH_MASS
from src.visualization.plot_2D import orbital_data_2D
from src.visualization.helpers import load_arrays, telemetry
from src.visualization.orbital_mechanics import orbital_mechanics

def animate_orbit(sat, step, dt):

    # -----------------------------
    # GATHER 3D DATA 
    # -----------------------------
    (trajectory3D, distance, velocity) = load_arrays(sat, step, dt)

    # -----------------------------
    # ORBITAL MECHANICS 
    # -----------------------------
    (perigee, apogee, a, b, xc, yc, zc, theta_xy, phi_z, e, e_vector, arc_progress, orbit_period) = orbital_mechanics(trajectory3D, distance)

    # -----------------------------
    # GATHER TELEMETRY DATA
    # -----------------------------
    (time_data, speed_data, speed_kmh_data, energy_mj_kg_data, momentum_data, grav_accel_data3D, grav_accel_norm_data, h) = telemetry(trajectory3D, distance, velocity, dt)

    # -----------------------------
    # GATHER 2D DATA
    # -----------------------------        
    (trajectory2D, grav_accel_data2D) = orbital_data_2D(trajectory3D, e_vector, h, grav_accel_data3D)

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
        QLabel {
            color: #E2E8F0;
        }
        QSplitter::handle {
            background-color: #1E293B;
        }
    """)

    pg.setConfigOptions(antialias=True)
    pg.setConfigOption('background', '#0B0F19')
    pg.setConfigOption('foreground', '#8A9AB2')
    pg.setConfigOptions(useOpenGL=True)

    win = QtWidgets.QMainWindow()
    win.setWindowTitle("Multi-View Orbital Dynamics Visualization")
    # Base resolution to help calculate proportions
    window_width, window_height = 1600, 1000 
    win.resize(window_width, window_height)
    
    central_widget = QtWidgets.QWidget()
    win.setCentralWidget(central_widget)
    main_layout = QtWidgets.QVBoxLayout(central_widget)
    main_layout.setContentsMargins(20, 20, 20, 20)
    
    # --- SPLITTER SETUP ---
    # 1. Main Vertical Splitter (Divides Top 60% and Bottom 40%)
    main_v_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
    main_layout.addWidget(main_v_splitter, stretch=1)

    # 2. Top Horizontal Splitter (Divides 3D View and 2D View)
    top_h_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
    main_v_splitter.addWidget(top_h_splitter)

    # 3. Bottom Horizontal Splitter (Divides Telemetry Plots and Info Text)
    bottom_h_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
    main_v_splitter.addWidget(bottom_h_splitter)

    # Set vertical proportions (60% Top / 40% Bottom)
    main_v_splitter.setSizes([int(window_height * 0.6), int(window_height * 0.4)])


    # ==========================================
    # TOP ROW (60% Height)
    # ==========================================

    # --- TOP LEFT: 3D VIEW (70% Width) ---
    view3d = gl.GLViewWidget()
    try:
        view3d.setBackgroundColor(QColor('#0B0F19'))
    except AttributeError:
        pass
    view3d.setCameraPosition(distance=max(a, b) * 2.5)
    top_h_splitter.addWidget(view3d)

    # --- TOP RIGHT: 2D VIEW (30% Width) ---
    glw_2d = pg.GraphicsLayoutWidget()
    ax_2d = glw_2d.addPlot(title="2D Trajectory Overview")
    top_h_splitter.addWidget(glw_2d)
    
    # Set horizontal proportions for Top Row (70% / 30%)
    top_h_splitter.setSizes([int(window_width * 0.7), int(window_width * 0.3)])


    # ==========================================
    # BOTTOM ROW (40% Height)
    # ==========================================

    # --- BOTTOM LEFT: TELEMETRY PLOTS (70% Width) ---
    glw_telemetry = pg.GraphicsLayoutWidget()
    ax_dist = glw_telemetry.addPlot(row=0, col=0, title="Altitude Over Time")
    ax_vel = glw_telemetry.addPlot(row=0, col=1, title="Velocity Over Time")
    bottom_h_splitter.addWidget(glw_telemetry)

    # --- BOTTOM RIGHT: TELEMETRY TEXT (30% Width) ---
    right_widget = QtWidgets.QWidget()
    right_layout = QtWidgets.QVBoxLayout(right_widget)
    right_layout.setContentsMargins(15, 10, 0, 0) # Top and Left margins
    
    info_label = QtWidgets.QLabel("")
    info_label.setFont(QtGui.QFont("Consolas", 11))
    info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
    right_layout.addWidget(info_label, stretch=1)
    
    bottom_h_splitter.addWidget(right_widget)

    # Set horizontal proportions for Bottom Row (70% / 30%)
    bottom_h_splitter.setSizes([int(window_width * 0.7), int(window_width * 0.3)])

    # Apply modern styling to all plot titles
    axis_font = QtGui.QFont("Segoe UI", 10)
    for plot in [ax_2d, ax_dist, ax_vel]:
        title_text = plot.titleLabel.text
        plot.setTitle(f'<span style="font-family: Segoe UI; font-size: 14pt; color: #E2E8F0;">{title_text}</span>')

    # Restart Button
    button_layout = QtWidgets.QHBoxLayout()
    restart_button = QtWidgets.QPushButton("RESTART SIMULATION")
    restart_button.setFixedWidth(250)
    restart_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
    button_layout.addStretch()
    button_layout.addWidget(restart_button)
    button_layout.addStretch()
    main_layout.addLayout(button_layout)


    # -----------------------------
    # 3D ORBIT PLOT CONFIGURATION 
    # -----------------------------
    earth_radius_km = EARTH_RADIUS * KM
    mesh_data = gl.MeshData.sphere(rows=400, cols=400, radius=earth_radius_km)
    try:
        from PIL import Image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        texture_path = os.path.join(current_dir, "earth_texture.jpg")
        
        img = Image.open(texture_path).convert('RGBA')
        
        img_data = np.array(img) / 255.0 
        h_img, w_img, _ = img_data.shape
        
        # Get sphere vertices
        vertices = mesh_data.vertexes()
        x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]

        # Normalize coordinates
        norm = np.sqrt(x**2 + y**2 + z**2)
        x_n, y_n, z_n = x / norm, y / norm, z / norm

        # Convert to texture coordinates
        u = (np.arctan2(y_n, x_n) + np.pi) / (2 * np.pi)
        v = (np.arcsin(z_n) + np.pi / 2) / np.pi

        pixel_x = np.clip((u * (w_img - 1)).astype(int), 0, w_img - 1)
        pixel_y = np.clip(((1 - v) * (h_img - 1)).astype(int), 0, h_img - 1)

        # Apply texture colors
        vertex_colors = img_data[pixel_y, pixel_x]
        mesh_data.setVertexColors(vertex_colors)

        earth_3d = gl.GLMeshItem(
            meshdata=mesh_data,
            smooth=True,
            shader="shaded",
            glOptions="opaque",
        )

        print("Successfully mapped 3D Earth texture!")

    except Exception as error:
        print(f"Could not load texture ({error}). Falling back to solid sphere.")

        earth_3d = gl.GLMeshItem(
            meshdata=mesh_data,
            smooth=True,
            color=pg.mkColor(59, 131, 245),
            shader="balloon",
            glOptions="opaque",
        )

    view3d.addItem(earth_3d)

    orbit_plot_3d = gl.GLLinePlotItem(
        pos=trajectory3D, 
        color=pg.mkColor(255, 255, 255), 
        width=1.5, 
        antialias=True,
        glOptions='opaque'
    )
    view3d.addItem(orbit_plot_3d)

    sat_point_3d = gl.GLScatterPlotItem(
        pos=np.array([trajectory3D[0]]), 
        color=(0.17, 0.83, 0.75, 1.0),
        size=15,
        glOptions='opaque'
    )
    view3d.addItem(sat_point_3d)

    g_vector_3d = gl.GLLinePlotItem(
        pos=np.array([[0,0,0], [0,0,0]]), 
        color=pg.mkColor('#EF4444'), 
        width=3, 
        antialias=True,
        glOptions='opaque'
    )
    view3d.addItem(g_vector_3d)

    # -----------------------------
    # 2D ORBIT PLOT CONFIGURATION 
    # -----------------------------
    ax_2d.setAspectLocked(True)
    ax_2d.setLabel('bottom', "x-axis [km]")
    ax_2d.setLabel('left', "y-axis [km]")
    ax_2d.getAxis('bottom').setTickFont(axis_font)
    ax_2d.getAxis('left').setTickFont(axis_font)
    ax_2d.showGrid(x=True, y=True, alpha=0.1)
    
    margin = 1.3 * max(a, b)
    ax_2d.setXRange(xc - margin, xc + margin)
    ax_2d.setYRange(yc - margin, yc + margin)

    earth_2d = QtWidgets.QGraphicsEllipseItem(-earth_radius_km, -earth_radius_km, earth_radius_km * 2, earth_radius_km * 2)
    earth_2d.setBrush(pg.mkBrush(QColor(30, 41, 59, 200))) 
    earth_2d.setPen(pg.mkPen(color='#3B82F6', width=2, style=QtCore.Qt.PenStyle.DashLine)) 
    ax_2d.addItem(earth_2d)

    ax_2d.plot(trajectory2D[:, 0], trajectory2D[:, 1], pen=pg.mkPen(color=(59, 130, 246, 150), width=1.5))

    ax_2d.plot([xc], [yc], pen=None, symbol='+', symbolPen="#FFFFFF", symbolSize=12)
    if np.linalg.norm(trajectory3D[-1]) >= EARTH_RADIUS * KM:
        ax_2d.plot([xc, xc + a*np.cos(theta_xy)], [yc, yc + a*np.sin(theta_xy)], pen=pg.mkPen('#10B981', style=QtCore.Qt.PenStyle.DotLine, width=1))
        ax_2d.plot([xc, xc + b*np.cos(theta_xy + np.pi/2)], [yc, yc + b*np.sin(theta_xy + np.pi/2)], pen=pg.mkPen('#F59E0B', style=QtCore.Qt.PenStyle.DotLine, width=1))
    

    sat_point_2d = ax_2d.plot([], [], pen=None, symbol='o', symbolBrush='#2DD4BF', symbolSize=10, symbolPen=pg.mkPen('#0B0F19', width=2))
    g_vector_2d = ax_2d.plot([], [], pen=pg.mkPen(color='#EF4444', width=2))

    # -----------------------------
    # TELEMETRY PLOTS CONFIGURATION 
    # -----------------------------
    ax_dist.setLabel('left', "Altitude [km]")
    ax_dist.setLabel('bottom', "Time [s]")
    ax_dist.getAxis('bottom').setTickFont(axis_font)
    ax_dist.getAxis('left').setTickFont(axis_font)
    ax_dist.setXRange(0, time_data[-1])
    ax_dist.setYRange(min(distance) * 0.9, max(distance) * 1.1)
    ax_dist.disableAutoRange()
    ax_dist.showGrid(x=True, y=True, alpha=0.1)
    ax_dist.getAxis('left').setWidth(70)
    
    curve_dist = ax_dist.plot(time_data, distance, pen=pg.mkPen(color='#10B981', width=2))
    curve_dist.setFillLevel(min(distance) * 0.8)
    curve_dist.setBrush(pg.mkBrush(QColor(16, 185, 129, 30))) 
    dist_point = ax_dist.plot([], [], pen=None, symbol='o', symbolBrush='#10B981', symbolSize=8, symbolPen=pg.mkPen('#0B0F19', width=1))

    ax_vel.setLabel('left', "Velocity [km/s]")
    ax_vel.setLabel('bottom', "Time [s]")
    ax_vel.getAxis('bottom').setTickFont(axis_font)
    ax_vel.getAxis('left').setTickFont(axis_font)
    ax_vel.setXRange(0, time_data[-1])
    ax_vel.setYRange(min(speed_data) * 0.9, max(speed_data) * 1.1)
    ax_vel.disableAutoRange()
    ax_vel.showGrid(x=True, y=True, alpha=0.1)
    ax_vel.getAxis('left').setWidth(70)
    
    curve_vel = ax_vel.plot(time_data, speed_data, pen=pg.mkPen(color='#F59E0B', width=2))
    curve_vel.setFillLevel(min(speed_data) * 0.8)
    curve_vel.setBrush(pg.mkBrush(QColor(245, 158, 11, 30))) 
    vel_point = ax_vel.plot([], [], pen=None, symbol='o', symbolBrush='#F59E0B', symbolSize=8, symbolPen=pg.mkPen('#0B0F19', width=1))

    # -----------------------------
    # ANIMATION  
    # -----------------------------
    finished = False
    animation_iterations = 0
    ui_iterations = 0
    animation_speed_multiplier = max(1, len(trajectory3D) // 1000)

    def update():
        nonlocal finished, animation_iterations, ui_iterations
        if finished:
            return

        if animation_iterations >= len(trajectory3D):
            animation_iterations = 0
            return
        
        # --- UPDATE 3D PLOT ---
        x3D, y3D, z3D = trajectory3D[animation_iterations]
            
        sat_point_3d.setData(pos=np.array([[x3D, y3D, z3D]]))

        gx3D, gy3D, gz3D = grav_accel_data3D[animation_iterations]
        quiver_scale_3d = a * 0.05 
        
        g_vector_3d.setData(pos=np.array([
            [x3D, y3D, z3D], 
            [x3D + gx3D * quiver_scale_3d, y3D + gy3D * quiver_scale_3d, z3D + gz3D * quiver_scale_3d]
        ]))

        # --- UPDATE 2D PLOT ---
        x2D, y2D = trajectory2D[animation_iterations]
        sat_point_2d.setData([x2D], [y2D])

        gx2D, gy2D = grav_accel_data2D[animation_iterations]
        quiver_scale_2d = a * 0.05
        g_vector_2d.setData([x2D, x2D + gx2D * quiver_scale_2d], [y2D, y2D + gy2D * quiver_scale_2d])

        # --- UPDATE TELEMETRY DATA ---
        current_time = time_data[animation_iterations]
        dist_point.setData([current_time], [distance[animation_iterations]])
        vel_point.setData([current_time], [speed_data[animation_iterations]])

        ui_iterations += 1
        if ui_iterations % 2 == 0:
            text_str = (
                f"Static information: \n"
                f"Eccentricity         : {e:.3f}\n"
                f"Apogee / Perigee     : {apogee:.0f} km / {perigee:.0f} km\n"
                f"Orbit Period         : {(orbit_period / 3600):.2f} h\n"
                f"Spec. Energy         : {energy_mj_kg_data[animation_iterations]:.2f} MJ/kg\n\n"
                f"Telemetry: \n"
                f"Speed                : {speed_kmh_data[animation_iterations]:,.0f} km/h\n"
                f"Altitude             : {distance[animation_iterations]:,.0f} km\n"
                f"Arc Progress         : {arc_progress[animation_iterations]*360:.1f}°\n"
                f"Ang. Momentum        : {momentum_data[animation_iterations]:.2e} m²/s\n"        
                f"Gravitational Accel. : {grav_accel_norm_data[animation_iterations]:.2f} m/s²\n"
            )
            info_label.setText(text_str)

        if animation_iterations == len(trajectory3D) - 1:
            animation_iterations += 1
        
        else:
            animation_iterations = min(animation_iterations + animation_speed_multiplier, len(trajectory3D) - 1)

        if np.linalg.norm(trajectory3D[animation_iterations]) <= EARTH_RADIUS * KM:
            print(np.linalg.norm(trajectory3D[animation_iterations]))
            print(EARTH_RADIUS * KM)
            finished = True

    def restart_animation():
        nonlocal finished, animation_iterations
        finished = False
        animation_iterations = 0

    restart_button.clicked.connect(restart_animation)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(16) 

    win.show()
    sys.exit(app.exec())

    return sat_point_3d, sat_point_2d, dist_point, vel_point, g_vector_2d, g_vector_3d, info_label, restart_button, win, app