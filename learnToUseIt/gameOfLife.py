import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Tamaño del grid
N = 50

def initialize_grid(N):
    """Inicializa el grid con valores aleatorios de 0 y 1."""
    return np.random.choice([0, 1], size=(N, N))

def update(grid):
    """Aplica las reglas del Juego de la Vida para actualizar el grid."""
    new_grid = grid.copy()
    for i in range(N):
        for j in range(N):
            total = int((grid[i, (j-1)%N] + grid[i, (j+1)%N] +
                         grid[(i-1)%N, j] + grid[(i+1)%N, j] +
                         grid[(i-1)%N, (j-1)%N] + grid[(i-1)%N, (j+1)%N] +
                         grid[(i+1)%N, (j-1)%N] + grid[(i+1)%N, (j+1)%N]))
            
            if grid[i, j] == 1:  # Celda viva
                if total < 2 or total > 3:
                    new_grid[i, j] = 0
            else:  # Celda muerta
                if total == 3:
                    new_grid[i, j] = 1
    return new_grid

# Inicialización del grid
grid = initialize_grid(N)

def animate(frame):
    global grid
    grid = update(grid)
    mat.set_data(grid)
    return [mat]

fig, ax = plt.subplots()
mat = ax.matshow(grid, cmap='gray')
ani = animation.FuncAnimation(fig, animate, frames=200, interval=100, blit=True)
plt.show()

