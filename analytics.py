def getAnalysisFromResult(history):
    """
    Analiza los resultados de las simulaciones y retorna un diccionario con los resultados.
    """
    # burnt_trees = sum(1 for state in history[-1].values() if state == "burnt")
    # total_steps = len(history)
    # full_burn_steps = next((i for i, state in enumerate(history) if all(v == "burnt" or v == "empty" for v in state.values())), total_steps)
    # max_fire_size = max(sum(1 for v in state.values() if v == "fire") for state in history)

    burnt_trees = 2
    total_steps = 2
    full_burn_steps = 2
    max_fire_size = 2

    return   (      
         burnt_trees,
         total_steps,
         full_burn_steps,
         max_fire_size
    )