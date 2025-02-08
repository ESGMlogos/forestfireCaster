import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time

EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3
G = None
states = None
spread = None
simulation = None
def spread_fire(states, G, spread):
    new_states = states.copy()
    fire_nodes = [node for node, state in states.items() if state == FIRE]
    for node in fire_nodes:
        for neighbor in G.neighbors(node):
            if states[neighbor] == TREE and random.random() < spread:
                new_states[neighbor] = FIRE
        new_states[node] = ASH
    return new_states

def run_simulation(id,forest, forestStates, prob_spread=0.5, max_steps=100):
    global G, states, spread, simulation   
    G = forest
    states = forestStates
    spread = prob_spread
    history = [states.copy()]

    for _ in range(max_steps):
        states = spread_fire(states, G, spread)
        history.append(states.copy())
        if all(state != FIRE for state in states.values()):
            break

    visualize_simulation(history,G,id)
    return history

def visualize_simulation(history, G, id):
    fig, ax = plt.subplots()
    pos = {(x, y): (x, -y) for x, y in G.nodes()}

    def update(frame):
        ax.clear()
        colors = ["white" if history[frame][node] == EMPTY else
                  "green" if history[frame][node] == TREE else
                  "red" if history[frame][node] == FIRE else "black"
                  for node in G.nodes()]
        nx.draw(G, pos=pos, node_color=colors, node_size=100, edge_color="gray", ax=ax)
        ax.set_title(f"Step {frame + 1} Simulation {id + 1}")
        if  frame + 1 == len(history) :
            ani.event_source.stop()           
            plt.close()

    ani = animation.FuncAnimation(fig, update, frames=len(history), interval=10, repeat=False)
    plt.show()


# def run_simulation(id,forest, forestStates, prob_spread=0.6, max_steps=100):
#     print("he llegado aqui 4")
#     global G, states, spread
#     G = forest
#     states = forestStates
#     spread = prob_spread
#     fig, ax = plt.subplots()
#     pos = {(x, y): (x, -y) for x, y in G.nodes()}
#     def update(frame):
#         global states
#         if all(state != FIRE for state in states.values()):
#             ani.event_source.stop()
#             plt.close()
#         ax.clear()
#         colors = ["white" if states[node] == EMPTY else
#         "green" if states[node] == TREE else
#         "red" if states[node] == FIRE else "black"
#         for node in G.nodes()]
#         nx.draw(G, pos=pos, node_color=colors, node_size=100, edge_color="gray", ax=ax)
#         ax.set_title(f"Step {frame + 1} Simulation {id + 1}")
#         states = spread_fire(states)
#         if  frame + 1 == max_steps :
#             ani.event_source.stop()           
#             plt.close()
        

#     ani = animation.FuncAnimation(fig, update, frames=max_steps, interval=20,repeat=False)
    
#     plt.show()
#     print("he llegado aqui")


# def spread_fire(states):
#     new_states = states.copy()
#     burning_trees = [node for node, state in states.items() if state == FIRE]
    
#     if not burning_trees:    
#         return states  # Stop if no trees are burning

#     for node in burning_trees:
#         if states[node] == FIRE:
#             for neighbor in G.neighbors(node):
#                 if states[neighbor] == TREE and random.random() < spread:
#                     new_states[neighbor] = FIRE
#             new_states[node] = ASH  # Se convierte en ceniza después de quemarse
#     return new_states