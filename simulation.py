import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time
from calculation import calculate_specific_probability
from analytics import collect_final_forests, generate_heat_map

EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3
EMPTY_COLOR, TREE_COLOR, FIRE_COLOR, ASH_COLOR = "white", "green", "red", "black"
EDGE_COLOR = "brown"

G = None
states = None
spread = None
simulation = None
def spread_fire(states, G, spread,weather_data):
    new_states = states.copy()
    fire_nodes = [node for node, state in states.items() if state == FIRE]
    for node in fire_nodes:
        for neighbor in G.neighbors(node):
            specific_spread = spread
            if weather_data and 1 == 2:
                specific_spread = calculate_specific_probability(weather_data, neighbor)

            if states[neighbor] == TREE and random.random() < specific_spread:
                new_states[neighbor] = FIRE
        new_states[node] = ASH
    return new_states

def run_simulation(forest, forestStates, prob_spread=0.5, max_steps=100,weather_data=None):
    global G, states, spread, simulation   
    G = forest
    states = forestStates
    spread = prob_spread
    history = [states.copy()]

    for _ in range(max_steps):
        states = spread_fire(states, G, spread,weather_data)
        history.append(states.copy())
        if all(state != FIRE for state in states.values()):
            break

    return history

def visualize_simulation(history, G, id, params, weather_data=None, save_path=None):
    fig, ax = plt.subplots()
    pos = {(x, y): (y, -x) for x, y in G.nodes()}

    def update(frame):
        ax.clear()
        colors = [EMPTY_COLOR if history[frame][node] == EMPTY else
                  TREE_COLOR if history[frame][node] == TREE else
                  FIRE_COLOR if history[frame][node] == FIRE else ASH_COLOR
                  for node in G.nodes()]
        nx.draw(G, pos=pos, node_color=colors, node_size=100, edge_color=EDGE_COLOR, ax=ax)
        ax.set_title(f"Step {frame + 1} Simulation {id + 1}")

        # Display weather parameters
        if weather_data:
            if params["simulation_mode"] == "hourly":
                time_index = frame % len(weather_data["hourly"]["time"])
                time = weather_data["hourly"]["time"][time_index]
                temperature = weather_data["hourly"]["temperature_2m"][time_index]
                wind_speed = weather_data["hourly"]["wind_speed_10m"][time_index]
                wind_direction = weather_data["hourly"]["wind_direction_10m"][time_index]
                fig.text(0.5, 0.01, f"Time: {time} | Temperature: {temperature}°C | Wind Speed: {wind_speed} km/h | Wind Direction: {wind_direction}°",
                         ha='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))
            elif params["simulation_mode"] == "daily":
                time_index = frame % len(weather_data["daily"]["time"])
                time = weather_data["daily"]["time"][time_index]
                temperature = weather_data["daily"]["apparent_temperature_min"][time_index]
                fig.text(0.5, 0.01, f"Date: {time} | Min Temperature: {temperature}°C",
                         ha='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

        if frame + 1 == len(history) and params["auto_close_simulations"]:
            ani.event_source.stop()
            plt.close()

    ani = animation.FuncAnimation(fig, update, frames=len(history), interval=10, repeat=False)
    if save_path:
        # Save the last frame as an image
        update(len(history) - 1)
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def save_simulation(history, G, id, save_path=None):
    # Create a new figure for the last frame
    fig, ax = plt.subplots(figsize=(16, 14))
    pos = {(x, y): (y, -x) for x, y in G.nodes()}
    colors = [EMPTY_COLOR if history[-1][node] == EMPTY else
              TREE_COLOR if history[-1][node] == TREE else
              FIRE_COLOR if history[-1][node] == FIRE else ASH_COLOR
              for node in G.nodes()]
    nx.draw(G, pos=pos, node_color=colors, node_size=306, edge_color=EDGE_COLOR, ax=ax)
    ax.set_title(f"Final State Simulation {id}", fontsize=36)

    # Save the plot
    if save_path:
        plt.savefig(save_path)
    plt.close()


def display_heat_map(csv_name, forest, save_path,plotShow=None):
    # Collect final forests
    final_forests = collect_final_forests(csv_name)

    # Generate heat map
    heat_map = generate_heat_map(final_forests)
    print("final forest")
    print(heat_map)

    #save heat map
    save_heatmap(csv_name,heat_map, forest,save_path)

    # Create a new figure for the heat map
    fig, ax = plt.subplots(figsize=(10, 7))
    pos = {(x, y): (y, -x) for x, y in forest.nodes()}  # Ensure pos includes all nodes in the forest
    colors = [heat_map.get(node, 0) for node in forest.nodes()]  # Use 0 for nodes not in heat_map
    nx.draw(forest, pos=pos, node_color=colors, node_size=100, edge_color=EDGE_COLOR, ax=ax, cmap=plt.cm.seismic)
    ax.set_title(f"Heat Map of Burnt Nodes for {csv_name}", fontsize=18)

    # Display the heat map
    if plotShow:
        plt.show()

    return fig, ax
def save_heatmap(csv_name,heat_map, forest,save_path):

    # Create a new figure for the heat map
    fig, ax = plt.subplots(figsize=(16, 14))
    pos = {(x, y): (y, -x) for x, y in forest.nodes()}  # Ensure pos includes all nodes in the forest
    colors = [heat_map.get(node, 0) for node in forest.nodes()]  # Use 0 for nodes not in heat_map
    nx.draw(forest, pos=pos, node_color=colors, node_size=306, edge_color=EDGE_COLOR, ax=ax, cmap=plt.cm.seismic)
    ax.set_title(f"Heat Map of Burnt Nodes for {csv_name}", fontsize=36)
    plt.savefig(save_path)
    plt.close()