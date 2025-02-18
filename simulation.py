import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time
from calculation import calculate_specific_probability

EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3
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
        colors = ["grey" if history[frame][node] == EMPTY else
                  "green" if history[frame][node] == TREE else
                  "red" if history[frame][node] == FIRE else "black"
                  for node in G.nodes()]
        nx.draw(G, pos=pos, node_color=colors, node_size=100, edge_color="gray", ax=ax)
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
        ani.save(save_path)
        plt.close()
    else:
        plt.show()
