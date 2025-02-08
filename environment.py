import networkx as nx
# import numpy as np
import random
from config import GRID_SIZE, INITIAL_FIRE_POINTS

# This could be on the config File, by know just leave it here
EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3


def generate_forest(grid_size=GRID_SIZE):
    """Generates a random forest with obstacles."""
    rows, cols = grid_size

    # forest = np.random.choice([EMPTY, TREE], size=(rows, cols), p=[0.2, 0.8])
    G = nx.grid_2d_graph(rows, cols)  # Lattice bidimensional
    states = {node: TREE for node in G.nodes()}
    
    # Place initial fire points
    fire_points = random.sample([(i, j) for i in range(rows) for j in range(cols) if states[(i, j)] == TREE], INITIAL_FIRE_POINTS)
    for i, j in fire_points:
        initial_fire = (i, j)
        states[initial_fire] = FIRE

    
    return G, states


