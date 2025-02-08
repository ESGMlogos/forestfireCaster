import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3

def spread_fire(states, prob_spread):
    new_states = states.copy()
    fire_indices = np.argwhere(states == FIRE)
    for x, y in fire_indices:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < states.shape[0] and 0 <= ny < states.shape[1]:
                if states[nx, ny] == TREE and random.random() < prob_spread:
                    new_states[nx, ny] = FIRE
        new_states[x, y] = ASH
    return new_states

def run_simulation(forest, prob_spread=0.5, max_steps=100):
    states = forest.copy()
    history = [states.copy()]

    for _ in range(max_steps):
        states = spread_fire(states, prob_spread)
        history.append(states.copy())
        if np.all(states != FIRE):
            break

    return history

def visualize_simulation(history, G):
    fig, ax = plt.subplots()
    pos = {(x, y): (x, -y) for x, y in G.nodes()}

    def update(frame):
        ax.clear()
        colors = ["white" if history[frame][x, y] == EMPTY else
                  "green" if history[frame][x, y] == TREE else
                  "red" if history[frame][x, y] == FIRE else "black"
                  for x, y in G.nodes()]
        nx.draw(G, pos=pos, node_color=colors, node_size=100, edge_color="gray", ax=ax)
        ax.set_title(f"Step {frame}")

    ani = animation.FuncAnimation(fig, update, frames=len(history), interval=200)
    plt.show()

# Example usage
forest = np.random.choice([EMPTY, TREE], size=(100, 100), p=[0.2, 0.8])
forest[50, 50] = FIRE  # Start fire in the middle

# Create a lattice graph
G = nx.grid_2d_graph(100, 100)
history = run_simulation(forest, prob_spread=0.3, max_steps=100)
visualize_simulation(history, G)
