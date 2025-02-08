import numpy as np

# Creamos una cuadrícula NumPy simple
Lattice = np.zeros((5,5))  # Un bosque vacío
Lattice[2,2] = 1  # Encendemos fuego en el centro

print(Lattice)

