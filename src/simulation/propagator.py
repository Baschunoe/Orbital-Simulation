import numpy as np
from scipy.integrate import solve_ivp
from src.physics.gravity import gravitational_acceleration

def orbit_differential_equation(t, y):
    """
    Die Differentialgleichung für den Löser.
    t: aktuelle Zeit (wird von RK45 intern genutzt)
    y: Zustandsvektor [rx, ry, rz, vx, vy, vz]
    """
    # 1. Zustand entpacken (Annahme: 3D-Simulation)
    position = y[:2]
    velocity = y[2:]
    
    # 2. Beschleunigung mit deiner vorhandenen Funktion berechnen
    accel = gravitational_acceleration(position)
    
    # 3. Ableitung zurückgeben: [Geschwindigkeit, Beschleunigung]
    # np.concatenate macht aus den zwei 3er-Arrays ein flaches 6er-Array
    return np.concatenate((velocity, accel))


def step(satellite, dt):
    """
    Bewegt den Satelliten um die Zeit dt in die Zukunft mittels RK45.
    """
    # 1. Den aktuellen Zustand in EINEN flachen Vektor packen
    y0 = np.concatenate((satellite.position, satellite.velocity))
    
    # 2. Das Anfangswertproblem von t=0 bis t=dt lösen
    # solve_ivp verwendet standardmäßig RK45
    solution = solve_ivp(
        fun=orbit_differential_equation, 
        t_span=(0, dt), 
        y0=y0,
        # optional: atol und rtol anpassen für mehr/weniger Präzision
        # rtol=1e-6, atol=1e-9 
    )
    
    # 3. Den neuen Zustand (am Ende des Zeitschritts dt) extrahieren.
    # solution.y enthält alle internen Schritte. Wir wollen den allerletzten:
    new_y = solution.y[:, -1]
    
    # 4. Werte wieder an das Satelliten-Objekt zurückgeben
    satellite.position = new_y[:2]
    satellite.velocity = new_y[2:]