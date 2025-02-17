import simulation
from config import GRID_SIZE
from analytics import getAnalysisFromResult
# def execute_simulation(simulation_id, forest, forest_state,prob_spread,num_iterations, wind_direction, wind_intensity, num_obstacles):
# def execute_simulation(simulation_id, forest, forest_state,prob_spread,num_iterations):
def execute_simulation(simulation_id, forest, forest_state, params, wheather_data=None):
    """
    Ejecuta una única simulación con los parámetros dados.

    Retorna:
        (id, árboles quemados, iteraciones hasta apagarse, iteraciones hasta quemar todo, tamaño del incendio más grande)
    """
    history = simulation.run_simulation(forest, forest_state, params["prob_spread"], params["num_iterations"],wheather_data)
    
    output = getAnalysisFromResult(history)
    
    if params["display_simulations"]: 
        simulation.visualize_simulation(history,forest,simulation_id,params,wheather_data)
    

    return (simulation_id,*output)
