import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time
from calculation import calculate_specific_probability
from analytics import collect_final_forests, generate_heat_map
from environment import getWeatherDataIteration
import gc

EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3
EMPTY_COLOR, TREE_COLOR, FIRE_COLOR, ASH_COLOR = "white", "green", "red", "black"
EDGE_COLOR = "brown"
LEGEND_ELEMENTS_SIMULATION = [
    plt.Line2D([0], [0], marker='o', color='w', label='Tree', markersize=10, markerfacecolor=TREE_COLOR),
    plt.Line2D([0], [0], marker='o', color='w', label='Fire', markersize=10, markerfacecolor=FIRE_COLOR),
    plt.Line2D([0], [0], marker='o', color='w', label='Ash', markersize=10, markerfacecolor=ASH_COLOR),
    plt.Line2D([0], [0], marker='o', color='w', label='Obstacle', markersize=10, markerfacecolor=EMPTY_COLOR)
]

G = None
states = None
spread = None
simulation = None
def spread_fire(states, G, spread,weather_data):
    new_states = states.copy()
    fire_nodes = [node for node, state in states.items() if state == FIRE]
    spread_probs = []
    for node in fire_nodes:
        for neighbor in G.neighbors(node):
            specific_spread = spread
            # if weather_data and 1 == 2:
            if weather_data:
                neighbors_list = list(G.neighbors(neighbor))
                neighbors_states = {node_neighbor :states[node_neighbor] for node_neighbor in neighbors_list}
                specific_spread = calculate_specific_probability(weather_data, spread ,neighbor, neighbors_states)
                spread_probs.append(specific_spread)

            if states[neighbor] == TREE and random.random() < specific_spread:
                new_states[neighbor] = FIRE
        new_states[node] = ASH
    spread_mean = np.mean(spread_probs) if spread_probs else spread
    return new_states, spread_mean

def run_simulation(forest, forestStates, prob_spread=0.5, max_steps=100,weather_data=None,params=None):
    global G, states, spread, simulation   
    G = forest
    states = forestStates
    spread = prob_spread
    history = [states.copy()]
    history_prob = [prob_spread]
    type =  params["simulation_mode"] if params else None;
    weather_params = params["hourly_params"] if type == "hourly" else params["daily_params"]

    for i in range(max_steps):
        weather_data_iteration = None
        if params["use_api_data"]:
            weather_data_iteration = getWeatherDataIteration(weather_data,type,weather_params,i)        
        states, specific_spread = spread_fire(states, G, spread,weather_data_iteration)
        history.append(states.copy())
        history_prob.append(specific_spread)
        # print(f"")
        # print(f" number of iterations {max_steps}")
        # print(f"Step {i} ")
        print(f"Probability Spread: {specific_spread}")
        # print(f"history lenght: {len(history)}")
        print(f"")
        if all(state != FIRE for state in states.values()):
            break

    return history, history_prob

def visualize_simulation(history, G, id, params, weather_data=None, history_prob=None ,save_path=None):
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
        # Add legend for node states
        legend_elements = LEGEND_ELEMENTS_SIMULATION
        ax.legend(handles=legend_elements, loc='upper right', title='Node States')

        # Add probability spread parameter as text annotation
        
        spread_display = history_prob[frame] if history_prob and frame < len(history_prob) else params["prob_spread"]
         
        ax.text(0.5, -0.005, f"Probability Spread: {spread_display}", ha='center', va='center', transform=ax.transAxes, fontsize=12, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))



        if frame + 1 == len(history) and params["auto_close_simulations"]:
            ani.event_source.stop()
            plt.close()

    ani = animation.FuncAnimation(fig, update, frames=len(history), interval=10, repeat=False)
    if save_path:
        # Save the last frame as an image
        update(len(history) - 1)
        plt.savefig(save_path)
        plt.close(fig)
    else:
        plt.show()
    # Explicitly delete large objects and call the garbage collector
    del fig, ax, pos, ani
    gc.collect()


def save_simulation(history, G, id, prob_spread,save_path=None):
    """ Saves the last frame of the simulation while ensuring memory is released properly. """

    try:
        # Create a new figure
        fig, ax = plt.subplots(figsize=(10, 8))  # Reduce size for efficiency
        pos = {(x, y): (y, -x) for x, y in G.nodes()}
        
        # Determine colors for nodes
        colors = [EMPTY_COLOR if history[-1][node] == EMPTY else
                  TREE_COLOR if history[-1][node] == TREE else
                  FIRE_COLOR if history[-1][node] == FIRE else ASH_COLOR
                  for node in G.nodes()]
        
        # Draw the network graph
        nx.draw(G, pos=pos, node_color=colors, node_size=150, edge_color=EDGE_COLOR, ax=ax)  # Reduce node size
        ax.set_title(f"Final State Simulation {id}", fontsize=20)  # Reduce font size
        
        # Add legend for node states
        legend_elements = LEGEND_ELEMENTS_SIMULATION
        ax.legend(handles=legend_elements, loc='upper right', title='Node States')

        # Add probability spread parameter as text annotation
        ax.text(0.5, -0.005, f"Probability Spread: {prob_spread}", ha='center', va='center', transform=ax.transAxes, fontsize=12, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))


        # Save the plot
        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')  # Reduce DPI for smaller files

        # **Forcefully clean up Matplotlib memory**
        plt.clf()      # Clear the figure
        plt.close(fig) # Close the figure
        plt.close('all')  # Close all figures in Matplotlib's memory
    finally:
        # Explicitly remove large objects
        del fig, ax, pos, colors, history
        gc.collect()  # Force garbage collection

def display_heat_map(csv_name, forest, save_path,plotShow=None, prob_spread=0.5):
    try:
        # Collect final forests
        final_forests = collect_final_forests(csv_name)

        # Generate heat map
        heat_map = generate_heat_map(final_forests)
        # print("final forest")
        # print(heat_map)

        #save heat map
        save_heatmap(csv_name,heat_map, forest,save_path, prob_spread)

        # Create a new figure for the heat map
        fig, ax = plt.subplots(figsize=(10, 7))
        pos = {(x, y): (y, -x) for x, y in forest.nodes()}  # Ensure pos includes all nodes in the forest
        colors = [heat_map.get(node, 0) for node in forest.nodes()]  # Use 0 for nodes not in heat_map
        nx.draw(forest, pos=pos, node_color=colors, node_size=100, edge_color=EDGE_COLOR, ax=ax, cmap=plt.cm.seismic)
        ax.set_title(f"Heat Map of Burnt Nodes for {csv_name}", fontsize=18)

        # Add colorbar for the heat map
        sm = plt.cm.ScalarMappable(cmap=plt.cm.seismic, norm=plt.Normalize(vmin=min(colors), vmax=max(colors)))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, shrink=0.5)
        cbar.set_label('Burnt Nodes Intensity')

        # Add legend for node states
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label='Fire', markersize=10, markerfacecolor=FIRE_COLOR),
            plt.Line2D([0], [0], marker='o', color='w', label='Obstacle', markersize=10, markerfacecolor=ASH_COLOR),
            plt.Line2D([0], [0], marker='o', color='w', label='Non Burned Tree', markersize=10, markerfacecolor=EMPTY_COLOR),
        ]
        ax.legend(handles=legend_elements, loc='upper right', title='Node States')

        # Add probability spread parameter as text annotation
        ax.text(0.5, -0.1, f"Probability Spread: {prob_spread}", ha='center', va='center', transform=ax.transAxes, fontsize=12, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))


        # Display the heat map
        if plotShow:
            plt.show()
         # **Forcefully clean up Matplotlib memory**
        plt.clf()      # Clear the figure
        plt.close(fig) # Close the figure
        plt.close('all')  # Close all figures in Matplotlib's memory

    finally:
        # Explicitly delete large objects and call the garbage collector
        del fig, ax, pos, colors, heat_map, final_forests
        gc.collect()
    
def save_heatmap(csv_name,heat_map, forest,save_path, prob_spread):

    try:
        # Create a new figure for the heat map
        fig, ax = plt.subplots(figsize=(16, 14))
        pos = {(x, y): (y, -x) for x, y in forest.nodes()}  # Ensure pos includes all nodes in the forest
        colors = [heat_map.get(node, 0) for node in forest.nodes()]  # Use 0 for nodes not in heat_map
        nx.draw(forest, pos=pos, node_color=colors, node_size=306, edge_color=EDGE_COLOR, ax=ax, cmap=plt.cm.seismic)
        ax.set_title(f"            Heat Map of Burnt Nodes for {csv_name}", fontsize=33)

        # Add colorbar for the heat map
        sm = plt.cm.ScalarMappable(cmap=plt.cm.seismic, norm=plt.Normalize(vmin=min(colors), vmax=max(colors)))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, shrink=0.7)
        cbar.set_label('Burnt Nodes Intensity')

        # Add legend for node states
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label='Fire', markersize=10, markerfacecolor=FIRE_COLOR),
            plt.Line2D([0], [0], marker='o', color='w', label='Obstacle', markersize=10, markerfacecolor=ASH_COLOR),
            plt.Line2D([0], [0], marker='o', color='w', label='Non Burned Tree', markersize=10, markerfacecolor=EMPTY_COLOR),
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 0.98), title='Node States')

        # Add probability spread parameter as text annotation
        ax.text(0.5, -0.005, f"Probability Spread: {prob_spread}", ha='center', va='center', transform=ax.transAxes, fontsize=24, bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))


        plt.savefig(save_path)
         # **Forcefully clean up Matplotlib memory**
        plt.clf()      # Clear the figure
        plt.close(fig) # Close the figure
        plt.close('all')  # Close all figures in Matplotlib's memory

    finally:
        # Explicitly delete large objects and call the garbage collector
        del fig, ax, pos, colors
        gc.collect()