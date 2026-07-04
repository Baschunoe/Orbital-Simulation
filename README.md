<div align="center">

# Orbital Simulation

A real-time satellite orbit simulator built with **Python**, combining classical orbital mechanics with an interactive visualization interface.

<!-- <img src="assets/demo.gif" width="900"/> -->

<br>

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Scientific_Computing-013243?style=for-the-badge&logo=numpy)
![License](https://img.shields.io/badge/License-MIT-black?style=for-the-badge)

</div>

---

## Overview

Orbital Simulation is an educational physics project that visualizes satellite motion around Earth using Newtonian gravity and numerical integration.

The project focuses on implementing the underlying physics from scratch while presenting the results through a clean desktop interface with real-time visualizations and orbital analytics.

<br>

## Features

<table>
<tr>
<td width="50%">

### Simulation

- Real-time orbit propagation
- RK4 numerical integration
- Newtonian gravity model
- Configurable initial conditions
- High-precision physics calculations

</td>

<td width="50%">

### Visualization

- Interactive 2D orbit view
- 3D Earth rendering
- Live trajectory tracking
- Real-time telemetry
- Dynamic orbital parameters

</td>
</tr>
</table>

<br>

## Gallery

<p align="center">

<img src="assets/main_window.png" width="48%"/>
<img src="assets/plots.png" width="48%"/>

</p>

<br>

## Orbital Parameters

The simulator continuously computes important orbital characteristics including

| Parameter | Description |
|-----------|-------------|
| Semi-major axis | Size of the orbit |
| Semi-minor axis | Orbit geometry |
| Eccentricity | Shape of the orbit |
| Perigee | Closest approach to Earth |
| Apogee | Farthest distance from Earth |
| Orbital Period | Estimated revolution time |
| Velocity | Instantaneous orbital speed |
| Angular Momentum | Conserved orbital quantity |
| Specific Orbital Energy | Mechanical energy per unit mass |

<br>

## Project Structure

```text
Orbital-Simulation/

├── main.py
├── requirements.txt
│
├── src/
│   ├── physics/
│   ├── simulation/
│   └── visualization/
│
├── assets/
└── notebooks/
```

<br>

## Getting Started

Clone the repository

```bash
git clone https://github.com/Baschunoe/Orbital-Simulation.git
cd Orbital-Simulation
```

Install the required packages

```bash
pip install -r requirements.txt
```

Run the application

```bash
python main.py
```

<br>

## Simulation Model

The simulator assumes

- Earth as the central gravitational body
- Newtonian gravitation
- No atmospheric drag
- No third-body perturbations
- Fourth-order Runge–Kutta integration

This provides a good balance between computational performance and physical accuracy for educational purposes.

<br>

## Built With

| | |
|:--|:--|
| Language | Python |
| GUI | PyQt6 |
| Numerical Computing | NumPy |
| Visualization | PyQtGraph |
| Physics | Custom implementation |

<br>

<details>

<summary><b>Future Ideas</b></summary>

<br>

- Multiple satellites
- Lunar and planetary gravity
- Atmospheric drag
- Orbit maneuvers
- Custom scenario editor
- Time acceleration
- Different numerical integrators
- Real satellite data import

</details>

<br>

## Motivation

This project started as a way to better understand orbital mechanics beyond the mathematical theory.

Rather than relying on an existing physics engine, the simulation implements the core mechanics manually—from gravitational acceleration and numerical integration to the computation of orbital elements—while providing an intuitive interface for exploring the results.

<br>

---

<div align="center">

Made as a learning project exploring **orbital mechanics**, **scientific computing**, and **interactive visualization**.

This ReadME was created and designed with the help of AI.

</div>