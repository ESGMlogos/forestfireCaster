import networkx as nx
# import numpy as np
import random
from config import GRID_SIZE, INITIAL_FIRE_POINTS
from calculation import calculate_general_probability


# This could be on the config File, by know just leave it here
EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3


def generate_forest(grid_size=GRID_SIZE, weather_data=None,params=None):
    """Generates a random forest with obstacles."""
    rows, cols = grid_size
    initial_fire_point_coordenates = params["fire_points"] if params and params["random_fire_start"] == False else None
    # forest = np.random.choice([EMPTY, TREE], size=(rows, cols), p=[0.2, 0.8])
    G = nx.grid_2d_graph(rows, cols)  # Lattice bidimensional
    states = {node: TREE for node in G.nodes()}

    # PLace obstacles points
    obstacles = params["num_obstacles"] if params else 0
    states = generateItemsInForest(grid_size,states, EMPTY, obstacles)
    
    # Place initial fire points
    fire_points = params["num_fire_points"] if params and params["random_fire_start"] == False else INITIAL_FIRE_POINTS
    states = generateItemsInForest(grid_size,states, FIRE, fire_points,initial_fire_point_coordenates)
    
    # Calculate general probability if weather data is provided
    prob_general = 0.5  # Default probability
    if weather_data and 1 == 2:
        prob_general = calculate_general_probability(weather_data)
        print("Esta es la probabilidad General")
        print(prob_general)
    
    return G, states, prob_general
    
def generateItemsInForest(grid_size,states, itemType, amount,coordenates=None):
    rows, cols = grid_size
    # Place initial fire points
    if coordenates:
        map_points = coordenates
    else:
        map_points = random.sample([(i, j) for i in range(rows) for j in range(cols) if states[(i, j)] == TREE], amount)

    for i, j in map_points:
        initial_fire = (i, j)
        states[initial_fire] = itemType
    return states

def getWeatherDataIteration(weather_data,type,params,iteration):
    weather_data_iteration = {}
    
    if type in ["hourly", "daily"]:
        time_index = iteration % len(weather_data["hourly"]["time"])
        weather_data_iteration["time"] = weather_data[type]["time"][time_index]
        for param, selected in params.items():
            if selected:
                weather_data_iteration[param] = weather_data[type][param][time_index]

    return weather_data_iteration