import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random

# Crear un lattice (rejilla) de tamaño N x N
N = 20  # Tamaño del bosque
G = nx.grid_2d_graph(N, N)  # Lattice bidimensional

# Asignar estados a los nodos
EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3
states = {node: TREE for node in G.nodes()}

# Encender fuego en un punto central
initial_fire = (N//2, N//2)
states[initial_fire] = FIRE

# Parámetros de propagación
prob_spread = 0.9  # Probabilidad de propagación del fuego

# Función de propagación

def spread_fire(states):
    new_states = states.copy()
    for node in states:
        if states[node] == FIRE:
            for neighbor in G.neighbors(node):
                if states[neighbor] == TREE and random.random() < prob_spread:
                    new_states[neighbor] = FIRE
            new_states[node] = ASH  # Se convierte en ceniza después de quemarse
    return new_states

# Simulación
steps = 3000
for t in range(steps):
    plt.figure(figsize=(6, 6))
    colors = ["white" if states[node] == EMPTY else
              "green" if states[node] == TREE else
              "red" if states[node] == FIRE else "black"
              for node in G.nodes()]
    nx.draw(G, pos={(x, y): (x, -y) for x, y in G.nodes()},
            node_color=colors, node_size=100, edge_color="gray")
    plt.title(f"Step {t}")
    plt.show()
    
    states = spread_fire(states)

