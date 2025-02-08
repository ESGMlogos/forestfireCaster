import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Estados de las celdas
EMPTY, TREE, FIRE = 0, 1, 2

# Parámetros del modelo
size = 50  # Tamaño del bosque
prob_spread = 0.3  # Probabilidad de propagación del fuego

# Inicialización del bosque
forest = np.random.choice([EMPTY, TREE], size=(size, size), p=[0.2, 0.8])
forest[size//2, size//2] = FIRE  # Iniciar fuego en el centro

def spread_fire(forest):
    """Propaga el fuego en el bosque según reglas de autómatas celulares."""
    new_forest = forest.copy()
    for i in range(1, size-1):
        for j in range(1, size-1):
            if forest[i, j] == FIRE:
                new_forest[i, j] = EMPTY  # Árbol quemado
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if forest[i+di, j+dj] == TREE and np.random.rand() < prob_spread:
                        new_forest[i+di, j+dj] = FIRE
    return new_forest

def update(frame):
    global forest
    forest = spread_fire(forest)
    mat.set_data(forest)
    return [mat]

fig, ax = plt.subplots()
mat = ax.matshow(forest, cmap='hot')
ani = animation.FuncAnimation(fig, update, frames=100, interval=20, blit=True)
plt.show()

