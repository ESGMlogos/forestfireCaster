import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
import networkx as nx
from tkinter import ttk, messagebox
import multiprocessing
import csv
import requests
from run_simulations import execute_simulation
from environment import generate_forest
from simulation import run_simulation
from simulation import visualize_simulation
from config import GRID_SIZE
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

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
        self.start_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.end_date = tk.StringVar(value=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        self.location = tk.StringVar()
        self.display_simulations = tk.BooleanVar(value=True)
        self.auto_close_simulations = tk.BooleanVar(value=True)
        self.custom_csv_name = tk.BooleanVar(value=False)
        self.csv_name = tk.StringVar(value="results.csv")
        self.simulation_mode = tk.StringVar(value="hourly")
        self.hourly_params = {
            "temperature_2m": tk.BooleanVar(value=True),
            "relative_humidity_2m": tk.BooleanVar(value=True),
            "wind_speed_10m": tk.BooleanVar(value=True),
            "wind_direction_10m": tk.BooleanVar(value=True),
            "soil_temperature_0_to_7cm": tk.BooleanVar(value=True),
            "soil_temperature_7_to_28cm": tk.BooleanVar(value=True)
        }
        self.daily_params = {
            "temperature_max_2m": tk.BooleanVar(value=True),
            "temperature_min_2m": tk.BooleanVar(value=True),
            "temperature_mean_2m": tk.BooleanVar(value=True),
            "wind_speed_max_10m": tk.BooleanVar(value=True),
            "wind_gust_max_10m": tk.BooleanVar(value=True),
            "wind_direction_dominant_10m": tk.BooleanVar(value=True),
            "shortwave_radiation_sum": tk.BooleanVar(value=True),
            "reference_evapotranspiration": tk.BooleanVar(value=True)
        }

        self.weather_data = None  # Variable to store weather data
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

        ttk.Label(frame, text="Start Date:").grid(row=6, column=0)
        ttk.Entry(frame, textvariable=self.start_date).grid(row=6, column=1)
        ttk.Label(frame, text="End Date:").grid(row=7, column=0)
        ttk.Entry(frame, textvariable=self.end_date).grid(row=7, column=1)
        ttk.Label(frame, text="Location:").grid(row=8, column=0)
        self.location_combobox = ttk.Combobox(frame, textvariable=self.location)
        self.location_combobox.grid(row=8, column=1)
        self.load_locations()
        ttk.Button(frame, text="Add Location", command=self.add_location).grid(row=8, column=2)
        ttk.Checkbutton(frame, text="Display Simulations", variable=self.display_simulations).grid(row=9, column=0, columnspan=2)
        ttk.Checkbutton(frame, text="Simulations not to close automatically", variable=self.auto_close_simulations).grid(row=10, column=0, columnspan=2)
        ttk.Checkbutton(frame, text="Custom CSV Name", variable=self.custom_csv_name, command=self.toggle_csv_name_entry).grid(row=11, column=0, columnspan=2)
        self.csv_name_entry = ttk.Entry(frame, textvariable=self.csv_name, state="disabled")
        self.csv_name_entry.grid(row=12, column=0, columnspan=2)
        ttk.Label(frame, text="Simulation Mode:").grid(row=13, column=0)
        ttk.Radiobutton(frame, text="Hourly", variable=self.simulation_mode, value="hourly").grid(row=13, column=1)
        ttk.Radiobutton(frame, text="Daily", variable=self.simulation_mode, value="daily").grid(row=13, column=2)
        ttk.Label(frame, text="Hourly Parameters:").grid(row=14, column=0, columnspan=2)
        for i, (param, var) in enumerate(self.hourly_params.items()):
            ttk.Checkbutton(frame, text=param.replace("_", " ").title(), variable=var).grid(row=15+i, column=0, columnspan=2)
        ttk.Label(frame, text="Daily Parameters:").grid(row=15+len(self.hourly_params), column=0, columnspan=2)
        for i, (param, var) in enumerate(self.daily_params.items()):
            ttk.Checkbutton(frame, text=param.replace("_", " ").title(), variable=var).grid(row=16+len(self.hourly_params)+i, column=0, columnspan=2)
        ttk.Button(frame, text="Run Simulations", command=self.run_simulations).grid(row=17+len(self.hourly_params)+len(self.daily_params), column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(frame, text="")
        self.result_label.grid(row=18+len(self.hourly_params)+len(self.daily_params), column=0, columnspan=2)

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

        self.result_frame = ttk.Frame(self.root)
        self.result_frame.grid(row=2, column=0, sticky="nsew")

    def load_locations(self):
        # Load locations from a CSV file
        try:
            with open("locations.csv", "r") as f:
                reader = csv.reader(f)
                locations = [row[0] for row in reader]
                self.location_combobox["values"] = locations
        except FileNotFoundError:
            self.location_combobox["values"] = []
    def add_location(self):
        # Add a new location to the CSV file
        new_location = self.location.get()
        if new_location:
            with open("locations.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([new_location])
            self.load_locations()
    def toggle_csv_name_entry(self):
        if self.custom_csv_name.get():
            self.csv_name_entry.config(state="normal")
        else:
            self.csv_name_entry.config(state="disabled")
    def fetch_weather_data(self, latitude, longitude, start_date, end_date, hourly_params, daily_params):
        base_url = "https://archive-api.open-meteo.com/v1/archive"
        hourly = ",".join([param for param, selected in hourly_params.items() if selected])
        daily = ",".join([param for param, selected in daily_params.items() if selected])
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": hourly,
            "daily": daily,
            "timezone": "GMT"
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            self.weather_data = response.json()
            print("Weather data fetched successfully")
        else:
            print("Failed to fetch weather data")
            self.weather_data = None

    def run_simulations(self):
        self.clear_simulations() 

        params = {
            "num_simulations": self.num_simulations.get(),
            "num_iterations": self.num_iterations.get(),
            "prob_spread": self.prob_spread.get(),
            "wind_direction": self.wind_direction.get(),
            "wind_intensity": self.wind_intensity.get(),
            "num_obstacles": self.num_obstacles.get(),
            "start_date": self.start_date.get(),
            "end_date": self.end_date.get(),
            "location": self.location.get(),
            "display_simulations": self.display_simulations.get(),
            "auto_close_simulations": self.auto_close_simulations.get(),
            "custom_csv_name": self.custom_csv_name.get(),
            "csv_name": self.csv_name.get(),
            "simulation_mode": self.simulation_mode.get(),
            "hourly_params": {k: v.get() for k, v in self.hourly_params.items()},
            "daily_params": {k: v.get() for k, v in self.daily_params.items()}
        }
        # Fetch weather data
        location = self.location.get()
        latitude, longitude = self.get_location_coordinates(location)
        self.fetch_weather_data(latitude, longitude, params["start_date"], params["end_date"], params["hourly_params"], params["daily_params"])

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
        self.save_results(results,params)

        self.result_label.config(text="Simulations completed. Results saved in results.csv")
        messagebox.showinfo("Success", "Simulations completed and saved!")
    
    def get_location_coordinates(self, location_name):
        with open("locations.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == location_name:
                    return float(row[1]), float(row[2])
        return None, None
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

    def save_results(self, results, params):
        # Clear the existing results section
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # Display the parameters
        ttk.Label(self.result_frame, text="Simulation Parameters", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        for i, (key, value) in enumerate(params.items()):
            ttk.Label(self.result_frame, text=f"{key}:").grid(row=i+1, column=0, sticky="e")
            ttk.Label(self.result_frame, text=f"{value}").grid(row=i+1, column=1, sticky="w")

        # Display the results
        ttk.Label(self.result_frame, text="Simulation Results", font=("Helvetica", 12, "bold")).grid(row=len(params)+1, column=0, columnspan=2, pady=10)
        headers = ["Simulation", "Burnt Trees", "Iterations to Extinguish", "Max Fire Size"]
        for j, header in enumerate(headers):
            ttk.Label(self.result_frame, text=header, font=("Helvetica", 10, "bold")).grid(row=len(params)+2, column=j, padx=5, pady=5)

        for i, result in enumerate(results):
            for j, value in enumerate(result):
                ttk.Label(self.result_frame, text=value).grid(row=len(params)+3+i, column=j, padx=5, pady=5)

        # Save the parameters and results to a CSV file
        with open("results.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Parameter", "Value"])
            for key, value in params.items():
                writer.writerow([key, value])
            writer.writerow([])  # Add an empty row for separation
            writer.writerow(headers)
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
