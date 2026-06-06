from src.physics.gravity import gravitational_acceleration

def step(satellite, dt):

    accel = gravitational_acceleration(
        satellite.position
    )

    satellite.velocity += accel * dt

    satellite.position += satellite.velocity * dt