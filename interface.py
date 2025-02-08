import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
import networkx as nx
from tkinter import ttk, messagebox
import multiprocessing
import csv
from run_simulations import execute_simulation
from environment import generate_forest
from simulation import run_simulation
from simulation import visualize_simulation
from config import GRID_SIZE
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3


class FireSimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Forest Fire Simulation")
        self.root.geometry("1200x800")  # Set the window size to 1200x800 pixels

        # Variables de entrada
        self.num_simulations = tk.IntVar(value=3)
        self.num_iterations = tk.IntVar(value=100)
        self.prob_spread = tk.DoubleVar(value=0.5)
        self.wind_direction = tk.StringVar(value="None")
        self.wind_intensity = tk.DoubleVar(value=0.0)
        self.num_obstacles = tk.IntVar(value=10)

        print("he llegado aqui 7")

        # Crear formulario
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky="W")

        ttk.Label(frame, text="Number of Simulations:").grid(row=0, column=0)
        ttk.Entry(frame, textvariable=self.num_simulations).grid(row=0, column=1)

        ttk.Label(frame, text="Iterations per Simulation:").grid(row=1, column=0)
        ttk.Entry(frame, textvariable=self.num_iterations).grid(row=1, column=1)

        ttk.Label(frame, text="Fire Spread Probability:").grid(row=2, column=0)
        ttk.Entry(frame, textvariable=self.prob_spread).grid(row=2, column=1)

        ttk.Label(frame, text="Wind Direction:").grid(row=3, column=0)
        ttk.Combobox(frame, textvariable=self.wind_direction, values=["None", "North", "South", "East", "West"]).grid(row=3, column=1)

        ttk.Label(frame, text="Wind Intensity:").grid(row=4, column=0)
        ttk.Entry(frame, textvariable=self.wind_intensity).grid(row=4, column=1)

        ttk.Label(frame, text="Number of Obstacles:").grid(row=5, column=0)
        ttk.Entry(frame, textvariable=self.num_obstacles).grid(row=5, column=1)

        ttk.Button(frame, text="Run Simulations", command=self.run_simulations).grid(row=6, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(frame, text="")
        self.result_label.grid(row=7, column=0, columnspan=2)

        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.grid(row=1, column=0, sticky="nsew")

        self.canvas = tk.Canvas(self.canvas_frame)
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def run_simulations(self):
        self.clear_simulations() 

        params = {
            "num_simulations": self.num_simulations.get(),
            "num_iterations": self.num_iterations.get(),
            "prob_spread": self.prob_spread.get(),
            "wind_direction": self.wind_direction.get(),
            "wind_intensity": self.wind_intensity.get(),
            "num_obstacles": self.num_obstacles.get(),
        }

        self.result_label.config(text="Running simulations...")
         # Ejecutar en paralelo
        G, states = generate_forest(GRID_SIZE)

        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())  # Usa todos los núcleos disponibles
        tasks = [(i,G,states,params["prob_spread"],params["num_iterations"]) for i in range(params["num_simulations"])]
        results = pool.starmap(execute_simulation, tasks)
        pool.close()
        pool.join()
        
        print("he llegado aqui 8")
        print(results)
        # pool = multiprocessing.Pool()
        # # graphs = [(i,G,states,params["prob_spread"],params["num_iterations"]) for i, result in enumerate(results)]
        # graphs = [(result['history'],G,i) for i, result in enumerate(results)]
        # pool.apply_async(visualize_simulation, (graphs,))
        # pool.close()
        # pool.join()

        # Guardar resultados
        # analitycs = getAnalysisFromResults(results)
        self.save_results(results)

        self.result_label.config(text="Simulations completed. Results saved in results.csv")
        messagebox.showinfo("Success", "Simulations completed and saved!")
    
    def visualize_simulation(self, history, G, id, frame):
        fig, ax = plt.subplots()
        pos = {(x, y): (x, -y) for x, y in G.nodes()}

        def update(frame):
            ax.clear()
            colors = ["white" if history[frame][node] == EMPTY else
                      "green" if history[frame][node] == TREE else
                      "red" if history[frame][node] == FIRE else "black"
                      for node in G.nodes()]
            nx.draw(G, pos=pos, node_color=colors, node_size=100, edge_color="gray", ax=ax)
            ax.set_title(f"Step {frame + 1} Simulation {id + 1}")
            if frame + 1 == len(history):
                ani.event_source.stop()
                plt.close(fig)

        ani = animation.FuncAnimation(fig, update, frames=len(history), interval=200, repeat=False)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def save_results(self, results):
        with open("results.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Simulation", "Burnt Trees", "Iterations to Extinguish", "Iterations to Full Burn", "Max Fire Size"])
            writer.writerows(results)

        self.result_label.config(text="Simulations completed. Results saved in results.csv")
        messagebox.showinfo("Success", "Simulations completed and saved!")
    def clear_simulations(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
if __name__ == "__main__":
    root = tk.Tk()
    app = FireSimulationApp(root)
    root.mainloop()
