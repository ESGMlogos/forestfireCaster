import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

N = 20  # Tamaño del bosque
G = nx.grid_2d_graph(N, N)  # Lattice bidimensional

# Asignar estados a los nodos
EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3
states = {node: TREE for node in G.nodes()}
initial_fire = (N//2, N//2)
states[initial_fire] = FIRE

prob_spread = 0.50  # Probabilidad de propagación del fuego

def spread_fire(states):
    new_states = states.copy()
    for node in states:
        if states[node] == FIRE:
            for neighbor in G.neighbors(node):
                if states[neighbor] == TREE and random.random() < prob_spread:
                    new_states[neighbor] = FIRE
            new_states[node] = ASH  # Se convierte en ceniza después de quemarse
    return new_states

fig, ax = plt.subplots()
pos = {(x, y): (x, -y) for x, y in G.nodes()}
def update(frame):
    global states
    ax.clear()
    colors = ["white" if states[node] == EMPTY else
              "green" if states[node] == TREE else
              "red" if states[node] == FIRE else "black"
              for node in G.nodes()]
    nx.draw(G, pos=pos, node_color=colors, node_size=100, edge_color="gray", ax=ax)
    ax.set_title(f"Step {frame}")
    states = spread_fire(states)

ani = animation.FuncAnimation(fig, update, frames=50, interval=200)
plt.show()

