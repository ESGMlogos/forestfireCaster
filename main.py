from config import GRID_SIZE
from environment import generate_forest
from simulation import run_simulation
# from visualization import animate_simulation

# Generate the forest with obstacles and trees
G, states = generate_forest(GRID_SIZE)

# Run the simulation
run_simulation(1,G, states)

# # Animate the simulation results
# animate_simulation(fire_history)
