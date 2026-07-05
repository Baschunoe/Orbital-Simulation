import sys
import os
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QColor

from src.physics.constants import EARTH_RADIUS, KM
from src.visualization.plot_2D import orbital_data_2D
from src.visualization.helpers import load_arrays, telemetry
from src.visualization.orbital_mechanics import orbital_mechanics

class OrbitalSimulationApp(QtWidgets.QMainWindow):
    def __init__(self, satellite, dt):
        super().__init__()
        self.sat = satellite
        self.dt = dt
        
        # State variables for animation
        self.finished = False
        self.animation_iterations = 0
        self.ui_iterations = 0
        self.axis_font = QtGui.QFont("Segoe UI", 10)
        
        self.setWindowTitle("Multi-View Orbital Dynamics Visualization")
        self.resize(1600, 1000)
        
        self.calculate_simulation_data()
        
        self.setup_ui()
        self.setup_3d_plot()
        self.setup_2d_plot()
        self.setup_telemetry_plots()
        
        # Setup Render Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16) 

    # -----------------------------
    # CALCULATE SIMULATION DATA
    # -----------------------------
    def calculate_simulation_data(self):
        
        self.trajectory3D, self.distance, self.velocity = load_arrays(self.sat, self.dt)
        
        (self.perigee, self.apogee, self.a, self.b, self.xc, self.yc, self.zc, 
         self.theta_xy, self.phi_z, self.e, self.e_vector, self.arc_progress, 
         self.orbit_period) = orbital_mechanics(self.trajectory3D, self.distance)
        
        (self.time_data, self.speed_data, self.speed_kmh_data, self.energy_mj_kg_data, 
         self.momentum_data, self.grav_accel_data3D, self.grav_accel_norm_data, 
         self.h) = telemetry(self.trajectory3D, self.distance, self.velocity, self.dt)
         
        self.trajectory2D, self.grav_accel_data2D = orbital_data_2D(
            self.trajectory3D, self.e_vector, self.h, self.grav_accel_data3D
        )
        
        self.animation_speed_multiplier = max(1, len(self.trajectory3D) // 1000)

    # -----------------------------
    # SETUP UI COMPONENTS
    # -----------------------------
    def setup_ui(self):
        
        self.setStyleSheet(
            "QMainWindow { background-color: #0B0F19; }\n"
            "QPushButton { background-color: #1E293B; color: #E2E8F0; border: 1px solid #334155; border-radius: 6px; padding: 12px; font-family: 'Segoe UI'; font-size: 14px; font-weight: bold; letter-spacing: 1px; }\n"
            "QPushButton:hover { background-color: #2DD4BF; color: #0B0F19; border: 1px solid #2DD4BF; }\n"
            "QLabel { color: #E2E8F0; }\n"
            "QSplitter::handle { background-color: #1E293B; }"
        )

        pg.setConfigOptions(antialias=True, background='#0B0F19', foreground='#8A9AB2', useOpenGL=True)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        main_v_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        main_layout.addWidget(main_v_splitter, stretch=1)

        self.top_h_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        main_v_splitter.addWidget(self.top_h_splitter)

        self.bottom_h_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        main_v_splitter.addWidget(self.bottom_h_splitter)

        main_v_splitter.setSizes([int(1000 * 0.6), int(1000 * 0.4)])
        
        # Telemetry Text Label
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        self.info_label = QtWidgets.QLabel("")
        self.info_label.setFont(QtGui.QFont("Consolas", 11))
        self.info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        right_layout.addWidget(self.info_label, stretch=1)
        self.bottom_h_splitter.addWidget(right_widget)
        
        # Restart Button
        button_layout = QtWidgets.QHBoxLayout()
        self.restart_button = QtWidgets.QPushButton("RESTART SIMULATION")
        self.restart_button.setFixedWidth(250)
        self.restart_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.restart_button.clicked.connect(self.restart_animation)
        button_layout.addStretch()
        button_layout.addWidget(self.restart_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    # -----------------------------
    # SETUP 3D PLOT
    # -----------------------------
    def setup_3d_plot(self):
        
        self.view3d = gl.GLViewWidget()
        self.view3d.setCameraPosition(distance=max(self.a, self.b) * 2.5)
        self.top_h_splitter.insertWidget(0, self.view3d)
        
        earth_radius_km = EARTH_RADIUS * KM
        mesh_data = gl.MeshData.sphere(rows=400, cols=400, radius=earth_radius_km)
        
        try:
            from PIL import Image
            texture_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "earth_texture.jpg")
            img_data = np.array(Image.open(texture_path).convert('RGBA')) / 255.0 
            
            # Map texture
            vertices = mesh_data.vertexes()
            x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
            norm = np.sqrt(x**2 + y**2 + z**2)
            u = (np.arctan2(y/norm, x/norm) + np.pi) / (2 * np.pi)
            v = (np.arcsin(z/norm) + np.pi / 2) / np.pi
            px = np.clip((u * (img_data.shape[1] - 1)).astype(int), 0, img_data.shape[1] - 1)
            py = np.clip(((1 - v) * (img_data.shape[0] - 1)).astype(int), 0, img_data.shape[0] - 1)
            mesh_data.setVertexColors(img_data[py, px])
            
            earth_3d = gl.GLMeshItem(meshdata=mesh_data, smooth=True, shader="shaded", glOptions="opaque")
        except Exception:
            earth_3d = gl.GLMeshItem(meshdata=mesh_data, smooth=True, color=pg.mkColor(59, 131, 245), shader="balloon", glOptions="opaque")

        self.view3d.addItem(earth_3d)

        mesh_data_moon = gl.MeshData.sphere(rows=200, cols=200, radius=1737.4)
        moon_3d = gl.GLMeshItem(meshdata=mesh_data_moon, smooth=True, color=pg.mkColor(200, 200, 200), shader="balloon", glOptions="opaque")
        moon_3d.translate(384400, 0, 0)
        self.view3d.addItem(moon_3d)

        # Plot Items
        self.view3d.addItem(gl.GLLinePlotItem(pos=self.trajectory3D, color=pg.mkColor(255, 255, 255), width=1.5, antialias=True, glOptions='opaque'))
        self.sat_point_3d = gl.GLScatterPlotItem(pos=np.array([self.trajectory3D[0]]), color=(0.17, 0.83, 0.75, 1.0), size=15, glOptions='opaque')
        self.view3d.addItem(self.sat_point_3d)
        
        self.g_vector_3d = gl.GLLinePlotItem(pos=np.array([[0,0,0], [0,0,0]]), color=pg.mkColor('#EF4444'), width=3, antialias=True, glOptions='opaque')
        self.view3d.addItem(self.g_vector_3d)

    # -----------------------------
    # SETUP 2D PLOT
    # -----------------------------
    def setup_2d_plot(self):
        
        glw_2d = pg.GraphicsLayoutWidget()
        self.ax_2d = glw_2d.addPlot(title='<span style="font-family: Segoe UI; font-size: 14pt; color: #E2E8F0;">2D Trajectory Overview</span>')
        self.top_h_splitter.insertWidget(1, glw_2d)
        self.top_h_splitter.setSizes([int(1600 * 0.7), int(1600 * 0.3)])
        
        self.ax_2d.setAspectLocked(True)
        self.ax_2d.setLabel('bottom', "x-axis [km]")
        self.ax_2d.setLabel('left', "y-axis [km]")
        self.ax_2d.showGrid(x=True, y=True, alpha=0.1)
        
        margin = 1.3 * max(self.a, self.b)
        self.ax_2d.setXRange(self.xc - margin, self.xc + margin)
        self.ax_2d.setYRange(self.yc - margin, self.yc + margin)

        # Earth and Static trajectories
        earth_rad = EARTH_RADIUS * KM
        earth_2d = QtWidgets.QGraphicsEllipseItem(-earth_rad, -earth_rad, earth_rad * 2, earth_rad * 2)
        earth_2d.setBrush(pg.mkBrush(QColor(30, 41, 59, 200))) 
        earth_2d.setPen(pg.mkPen(color='#3B82F6', width=2, style=QtCore.Qt.PenStyle.DashLine)) 
        self.ax_2d.addItem(earth_2d)

        self.ax_2d.plot(self.trajectory2D[:, 0], self.trajectory2D[:, 1], pen=pg.mkPen(color=(59, 130, 246, 150), width=1.5))
        self.ax_2d.plot([self.xc], [self.yc], pen=None, symbol='+', symbolPen="#FFFFFF", symbolSize=12)

        self.ax_2d.plot([self.xc + self.a], [self.yc], pen=None, symbol='o', symbolBrush='#FACC15', symbolSize=10)
        self.ax_2d.plot([self.xc], [self.yc + self.b], pen=None, symbol='o', symbolBrush='#FACC15', symbolSize=10)
        self.ax_2d.plot([self.xc - self.a], [self.yc], pen=None, symbol='o', symbolBrush='#FACC15', symbolSize=10)
        self.ax_2d.plot([self.xc], [self.yc - self.b], pen=None, symbol='o', symbolBrush='#FACC15', symbolSize=10)
        
        self.sat_point_2d = self.ax_2d.plot([], [], pen=None, symbol='o', symbolBrush='#2DD4BF', symbolSize=10, symbolPen=pg.mkPen('#0B0F19', width=2))
        self.g_vector_2d = self.ax_2d.plot([], [], pen=pg.mkPen(color='#EF4444', width=2))

    # -----------------------------
    # SETUP TELEMETRY PLOTS
    # -----------------------------
    def setup_telemetry_plots(self):
        
        glw_telemetry = pg.GraphicsLayoutWidget()
        self.bottom_h_splitter.insertWidget(0, glw_telemetry)
        self.bottom_h_splitter.setSizes([int(1600 * 0.7), int(1600 * 0.3)])

        self.ax_dist = glw_telemetry.addPlot(row=0, col=0, title='<span style="font-family: Segoe UI; font-size: 14pt; color: #E2E8F0;">Altitude Over Time</span>')
        self.ax_vel = glw_telemetry.addPlot(row=0, col=1, title='<span style="font-family: Segoe UI; font-size: 14pt; color: #E2E8F0;">Velocity Over Time</span>')
        
        for ax in [self.ax_dist, self.ax_vel]:
            ax.setLabel('bottom', "Time [s]")
            ax.setXRange(0, self.time_data[-1])
            ax.disableAutoRange()
            ax.showGrid(x=True, y=True, alpha=0.1)

        self.ax_dist.setYRange(min(self.distance) * 0.9, max(self.distance) * 1.1)
        curve_dist = self.ax_dist.plot(self.time_data, self.distance, pen=pg.mkPen(color='#10B981', width=2))
        curve_dist.setFillLevel(min(self.distance) * 0.8)
        curve_dist.setBrush(pg.mkBrush(QColor(16, 185, 129, 30))) 
        self.dist_point = self.ax_dist.plot([], [], pen=None, symbol='o', symbolBrush='#10B981', symbolSize=8)

        self.ax_vel.setYRange(min(self.speed_data) * 0.9, max(self.speed_data) * 1.1)
        curve_vel = self.ax_vel.plot(self.time_data, self.speed_data, pen=pg.mkPen(color='#F59E0B', width=2))
        curve_vel.setFillLevel(min(self.speed_data) * 0.8)
        curve_vel.setBrush(pg.mkBrush(QColor(245, 158, 11, 30))) 
        self.vel_point = self.ax_vel.plot([], [], pen=None, symbol='o', symbolBrush='#F59E0B', symbolSize=8)

    # -----------------------------
    # UPDATE FRAME
    # -----------------------------
    def update_frame(self):
        
        if self.finished:
            return

        idx = self.animation_iterations
        if idx >= len(self.trajectory3D):
            self.animation_iterations = 0
            idx = 0
        
        # 3D
        x3D, y3D, z3D = self.trajectory3D[idx]
        self.sat_point_3d.setData(pos=np.array([[x3D, y3D, z3D]]))
        
        gx3D, gy3D, gz3D = self.grav_accel_data3D[idx]
        qs_3d = self.a * 0.05 
        self.g_vector_3d.setData(pos=np.array([[x3D, y3D, z3D], [x3D + gx3D*qs_3d, y3D + gy3D*qs_3d, z3D + gz3D*qs_3d]]))

        # 2D
        x2D, y2D = self.trajectory2D[idx]
        self.sat_point_2d.setData([x2D], [y2D])
        gx2D, gy2D = self.grav_accel_data2D[idx]
        qs_2d = self.a * 0.05
        self.g_vector_2d.setData([x2D, x2D + gx2D * qs_2d], [y2D, y2D + gy2D * qs_2d])

        # Telemetry
        c_time = self.time_data[idx]
        self.dist_point.setData([c_time], [self.distance[idx]])
        self.vel_point.setData([c_time], [self.speed_data[idx]])

        # Info Update (Staggered to save CPU)
        self.ui_iterations += 1
        if self.ui_iterations % 2 == 0:
            text_str = (
                f"Static information: \n"
                f"Eccentricity         : {self.e:.3f}\n"
                f"Apogee / Perigee     : {self.apogee:.0f} km / {self.perigee:.0f} km\n"
                f"Orbit Period         : {(self.orbit_period / 3600):.2f} h\n"
                f"Spec. Energy         : {self.energy_mj_kg_data[idx]:.2f} MJ/kg\n\n"
                f"Telemetry: \n"
                f"Speed                : {self.speed_kmh_data[idx]:,.0f} km/h\n"
                f"Altitude             : {self.distance[idx]:,.0f} km\n"
                f"Arc Progress         : {self.arc_progress[idx]*360:.1f}°\n"
                f"Ang. Momentum        : {self.momentum_data[idx]:.2e} m²/s\n"        
                f"Gravitational Accel. : {self.grav_accel_norm_data[idx]:.2f} m/s²\n"
            )
            self.info_label.setText(text_str)

        if idx == len(self.trajectory3D) - 1:
            self.animation_iterations += 1
        else:
            self.animation_iterations = min(idx + self.animation_speed_multiplier, len(self.trajectory3D) - 1)

        if np.linalg.norm(self.trajectory3D[idx]) <= EARTH_RADIUS * KM:
            self.finished = True

    # -----------------------------
    # RESTART ANIMATION
    # -----------------------------
    def restart_animation(self):
        
        self.finished = False
        self.animation_iterations = 0

# -----------------------------
# LAUNCHER
# -----------------------------
def start_application(satellite, dt):
    
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        
    window = OrbitalSimulationApp(satellite, dt)
    window.show()
    sys.exit(app.exec())