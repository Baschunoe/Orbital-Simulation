import numpy as np

class Satellite:

    def __init__(self, position, velocity):

        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)