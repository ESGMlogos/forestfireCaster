import multiprocessing
import simulation
from config import GRID_SIZE
from environment import generate_forest
from analytics import getAnalysisFromResult
# def execute_simulation(simulation_id, forest, forest_state,prob_spread,num_iterations, wind_direction, wind_intensity, num_obstacles):
def execute_simulation(simulation_id, forest, forest_state,prob_spread,num_iterations):
    """
    Ejecuta una única simulación con los parámetros dados.

    Retorna:
        (id, árboles quemados, iteraciones hasta apagarse, iteraciones hasta quemar todo, tamaño del incendio más grande)
    """
    history = simulation.run_simulation(simulation_id,forest, forest_state, prob_spread, num_iterations)
    
    output = getAnalysisFromResult(history)


    return (simulation_id,*output)

def execute_simulations(params):
    """
    Ejecuta múltiples simulaciones en paralelo con los parámetros dados.

    Retorna una lista de resultados de simulaciones.
    """
    G, states = generate_forest(GRID_SIZE)


    # num_simulations = params["num_simulations"]
    # num_iterations = params["num_iterations"]
    # prob_spread = params["prob_spread"]
    # wind_direction = params["wind_direction"]
    # wind_intensity = params["wind_intensity"]
    # num_obstacles = params["num_obstacles"]
# 
    # pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())  # Usa todos los núcleos disponibles
    # tasks = [(i, num_iterations, prob_spread, wind_direction, wind_intensity, num_obstacles) for i in range(num_simulations)]
    # 
    # results = pool.starmap(execute_simulation, tasks)
    # pool.close()
    # pool.join()
# 
    # return results

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())  # Usa todos los núcleos disponibles
    tasks = [(i,G,states,params["prob_spread"],params["num_iterations"]) for i in range(params["num_simulations"])]
    results = pool.starmap(execute_simulation, tasks)
    pool.close()
    pool.join()

    return results
