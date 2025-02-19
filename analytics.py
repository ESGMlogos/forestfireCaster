import json
import os
EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3

def getAnalysisFromResult(history):
    """
    Analiza los resultados de las simulaciones y retorna una tupla con los resultados.
    """

    burnt_trees = sum(1 for state in history[-1].values() if state == ASH)
    total_steps = len(history)
    max_fire_size = max(len(fire) for fire in getFires(history[-1]))

    return   (      
         burnt_trees,
         total_steps,
         max_fire_size
    )

def getFires(states):
     fires = []
     burnt_trees = [ node for node, state in states.items() if state == ASH]

     while burnt_trees:
          fire = []
          fire, burnt_trees = getFire(fire, burnt_trees, burnt_trees[0])
          fires.append(fire)
     return fires

def getFire(fire,burnt_trees,tree):
     if tree not in burnt_trees and tree in fire:
          return fire, burnt_trees     
     fire.append(tree)
     burnt_trees.remove(tree)
     for neighbor in getBurntNeighbors(burnt_trees,tree):
        fire, burnt_trees = getFire(fire, burnt_trees, neighbor)
     return fire, burnt_trees

def getBurntNeighbors(burnt_trees,tree):
     row , column = tree
     neighbors = [(row + 1, column), (row - 1, column),(row, column + 1), (row, column - 1)]
     burnt_neighbors = [node for node in neighbors if node in burnt_trees]
     return burnt_neighbors



def read_final_forest(file_path):
    with open(file_path, "r") as f:
        final_forest_str_keys = json.load(f)
    
    # Convert keys back to tuples
    final_forest = {eval(key): value for key, value in final_forest_str_keys.items()}
    return final_forest

def collect_final_forests(csv_name):
    # Determine the folder name
    simulation_folder = os.path.join("CSVs", csv_name, "LastIteration")

    # Initialize an array to store all final forests
    final_forests = []

    # Iterate over each file in the folder
    for file_name in os.listdir(simulation_folder):
        if file_name.endswith(".txt"):
            file_path = os.path.join(simulation_folder, file_name)
            final_forest = read_final_forest(file_path)
            final_forests.append(final_forest)

    return final_forests

def generate_heat_map(final_forests):
    # Initialize the heat map with zeros
    heat_map = {}

    # Iterate over each final forest
    for final_forest in final_forests:
        for node, state in final_forest.items():
               if state == FIRE or state == ASH:  # Consider burnt nodes
                    if node not in heat_map:
                         heat_map[node] = 0
                    heat_map[node] += 1
               elif state == EMPTY:
                    if node not in heat_map:
                         heat_map[node] = 0
                    heat_map[node] -= 1
          

    return heat_map