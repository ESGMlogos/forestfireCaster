import networkx as nx
import matplotlib.pyplot as plt

# Creamos un lattice 2D con interacciones explícitas
G = nx.grid_2d_graph(5, 5)  # Una cuadrícula de 5x5 con conexiones explícitas

# Dibujamos el lattice
nx.draw(G, with_labels=True, node_color="lightblue", edge_color="gray")
plt.show()

