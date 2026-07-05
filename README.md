<div align="center">

# Orbital Simulation

A modern desktop application for visualizing Earth satellite orbits using **numerical orbital mechanics**, **adaptive integration**, and an interactive multi-view interface.

<!-- <img src="assets/demo.gif" width="900"/> -->

<br>

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Scientific_Computing-013243?style=for-the-badge&logo=numpy)
![SciPy](https://img.shields.io/badge/SciPy-Numerical_Integration-8CAAE6?style=for-the-badge&logo=scipy)
![License](https://img.shields.io/badge/License-MIT-black?style=for-the-badge)

</div>

---

# Overview

Orbital Simulation is an educational project that models satellite motion around Earth using Newtonian gravity and adaptive numerical integration.

The application combines accurate physics calculations with a responsive desktop interface featuring synchronized 3D visualization, orbital-plane projection, telemetry plots, and automatically computed orbital parameters.

Rather than relying on an external physics engine, every aspect of the orbital dynamics—from gravitational acceleration to trajectory propagation and orbital analysis—is implemented from first principles.

---

# Features

<table>
<tr>
<td width="50%">

### Physics Engine

- Adaptive RK45 orbit propagation (SciPy)
- Newtonian point-mass gravity
- Automatic orbital period estimation
- Collision detection with Earth
- High-precision numerical integration

</td>

<td width="50%">

### Visualization

- Interactive 3D Earth visualization
- Textured Earth rendering
- Moon reference model
- 2D orbital-plane projection
- Animated satellite tracking
- Gravity vector visualization
- Live telemetry dashboard

</td>
</tr>
</table>

---

# Gallery

<p align="center">

<img src="assets/main_window.png" width="48%"/>
<img src="assets/plots.png" width="48%"/>

</p>

---

# Live Telemetry

During the simulation the application continuously updates

| Quantity | Description |
|-----------|-------------|
| Altitude | Distance above Earth's surface |
| Velocity | Current orbital speed |
| Specific Orbital Energy | Mechanical energy per unit mass |
| Angular Momentum | Conserved orbital quantity |
| Gravitational Acceleration | Instantaneous acceleration |
| Arc Progress | Position along the orbit |
| Orbit Period | Estimated revolution time |

---

# Orbital Analysis

After propagating the trajectory, the simulator derives important orbital properties directly from the computed orbit.

These include

- Semi-major axis
- Semi-minor axis
- Eccentricity
- Perigee
- Apogee
- Orbit center
- Orbital orientation
- Orbital period

---

# Project Structure

```text
Orbital-Simulation/

├── main.py
├── requirements.txt
│
├── src/
│   ├── physics/
│   │   ├── constants.py
│   │   └── gravity.py
│   │
│   ├── simulation/
│   │   ├── propagator.py
│   │   └── satellite.py
│   │
│   └── visualization/
│       ├── helpers.py
│       ├── layout.py
│       ├── orbital_mechanics.py
│       └── plot_2D.py
│
└── assets/
```

---

<!--
## Getting Started

```bash
git clone https://github.com/Baschunoe/Orbital-Simulation.git
cd Orbital-Simulation

pip install -r requirements.txt

python main.py
```
-->

# Simulation Model

The simulation assumes

- Earth as the only gravitating body
- Newtonian gravity
- No atmospheric drag
- No third-body perturbations
- No solar radiation pressure
- Adaptive RK45 numerical integration

---

# Built With

| | |
|:--|:--|
| Language | Python |
| GUI | PyQt6 |
| Numerical Computing | NumPy |
| Scientific Computing | SciPy |
| Visualization | PyQtGraph |
| Physics | Custom implementation |

---

<details>

<summary><b>Future Ideas</b></summary>

<br>

- Real-time propagation
- Multiple satellites
- Lunar and planetary gravity
- Atmospheric drag
- Orbit maneuvers
- Ground-track visualization
- Orbital elements editor
- Simulation controls (pause, speed, rewind)
- Export telemetry data

</details>

---

# Motivation

This project began as a way to gain a deeper understanding of orbital mechanics by implementing the underlying physics instead of relying on existing simulation engines.

It evolved into a complete interactive visualization tool capable of numerically propagating satellite trajectories, computing orbital characteristics, and presenting the results through synchronized 2D and 3D visualizations together with real-time telemetry.

The focus of the project is educational: demonstrating how classical mechanics, numerical methods, and scientific visualization work together to model orbital motion.

---

<div align="center">

Made as a learning project exploring **orbital mechanics**, **scientific computing**, **numerical integration**, and **interactive visualization**.

This README was designed with the assistance of AI.

</div>