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
