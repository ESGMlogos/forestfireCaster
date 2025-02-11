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
from dateutil.relativedelta import relativedelta

EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3

class FireSimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Forest Fire Simulation")
        self.root.geometry("1270x630")  # Set the window size to 1200x800 pixels

        # Variables de entrada
        self.num_simulations = tk.IntVar(value=2)
        self.num_iterations = tk.IntVar(value=100)
        self.prob_spread = tk.DoubleVar(value=0.1)
        self.wind_direction = tk.StringVar(value="None")
        self.wind_intensity = tk.DoubleVar(value=0.0)
        self.num_obstacles = tk.IntVar(value=10)
        self.start_date = tk.StringVar(value=(datetime.now() - relativedelta(years=10)).strftime("%Y-%m-%d"))
        self.end_date = tk.StringVar(value=(datetime.now() - relativedelta(years=10) + timedelta(days=1)).strftime("%Y-%m-%d"))
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
            "temperature_2m_max": tk.BooleanVar(value=True),
            "temperature_2m_min": tk.BooleanVar(value=True),
            "temperature_2m_mean": tk.BooleanVar(value=True),
            "wind_speed_10m_max": tk.BooleanVar(value=True),
            "wind_gusts_10m_max": tk.BooleanVar(value=True),
            "wind_direction_10m_dominant": tk.BooleanVar(value=True),
            "shortwave_radiation_sum": tk.BooleanVar(value=True),
            "et0_fao_evapotranspiration": tk.BooleanVar(value=True)
        }

        self.weather_data = None  # Variable to store weather data

        print("he llegado aqui 7")

        # Crear formulario
        self.create_widgets()

    def create_widgets(self):
        # Configure the main grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create a main frame with a scrollbar
        main_canvas = tk.Canvas(self.root)
        main_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        main_scrollable_frame = ttk.Frame(main_canvas)

        main_scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(
                scrollregion=main_canvas.bbox("all")
            )
        )

        main_canvas.create_window((0, 0), window=main_scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)

        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")

        # Left Column
        left_frame = ttk.Frame(main_scrollable_frame)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Input Parameters Block
        input_frame = ttk.LabelFrame(left_frame, text="Simulation Parameters", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(input_frame, text="Number of Simulations:").grid(row=0, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.num_simulations).grid(row=0, column=1, sticky="ew")

        ttk.Label(input_frame, text="Iterations per Simulation:").grid(row=1, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.num_iterations).grid(row=1, column=1, sticky="ew")

        ttk.Label(input_frame, text="Fire Spread Probability:").grid(row=2, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.prob_spread).grid(row=2, column=1, sticky="ew")

        ttk.Label(input_frame, text="Wind Direction:").grid(row=3, column=0, sticky="w")
        ttk.Combobox(input_frame, textvariable=self.wind_direction, values=["None", "North", "South", "East", "West"]).grid(row=3, column=1, sticky="ew")

        ttk.Label(input_frame, text="Wind Intensity:").grid(row=4, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.wind_intensity).grid(row=4, column=1, sticky="ew")

        ttk.Label(input_frame, text="Number of Obstacles:").grid(row=5, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.num_obstacles).grid(row=5, column=1, sticky="ew")

        ttk.Label(input_frame, text="Start Date:").grid(row=6, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.start_date).grid(row=6, column=1, sticky="ew")

        ttk.Label(input_frame, text="End Date:").grid(row=7, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.end_date).grid(row=7, column=1, sticky="ew")

        ttk.Label(input_frame, text="Location:").grid(row=8, column=0, sticky="w")
        self.location_combobox = ttk.Combobox(input_frame, textvariable=self.location)
        self.location_combobox.grid(row=8, column=1, sticky="ew")
        self.load_locations()

        ttk.Button(input_frame, text="Add Location", command=self.add_location).grid(row=8, column=2, sticky="ew")

        ttk.Checkbutton(input_frame, text="Display Simulations", variable=self.display_simulations).grid(row=9, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(input_frame, text="Simulations not to close automatically", variable=self.auto_close_simulations).grid(row=10, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(input_frame, text="Custom CSV Name", variable=self.custom_csv_name, command=self.toggle_csv_name_entry).grid(row=11, column=0, columnspan=2, sticky="w")
        self.csv_name_entry = ttk.Entry(input_frame, textvariable=self.csv_name, state="disabled")
        self.csv_name_entry.grid(row=12, column=0, columnspan=2, sticky="ew")

        ttk.Label(input_frame, text="Simulation Mode:").grid(row=13, column=0, sticky="w")
        ttk.Radiobutton(input_frame, text="Hourly", variable=self.simulation_mode, value="hourly").grid(row=13, column=1, sticky="w")
        ttk.Radiobutton(input_frame, text="Daily", variable=self.simulation_mode, value="daily").grid(row=13, column=2, sticky="w")

        
        ttk.Button(left_frame, text="Run Simulations", command=self.run_simulations).grid(row=1, column=0, pady=10, sticky="ew")

        self.result_label = ttk.Label(left_frame, text="")
        self.result_label.grid(row=2, column=0, pady=10, sticky="ew")

        # Weather Parameters Block
        params_frame = ttk.LabelFrame(left_frame, text="Weather Parameters", padding=10)
        params_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        # Hourly Parameters
        hourly_frame = ttk.LabelFrame(params_frame, text="Hourly Parameters", padding=10)
        hourly_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        for i, (param, var) in enumerate(self.hourly_params.items()):
            ttk.Checkbutton(hourly_frame, text=param.replace("_", " ").title(), variable=var).grid(row=i, column=0, sticky="w")

        # Daily Parameters
        daily_frame = ttk.LabelFrame(params_frame, text="Daily Parameters", padding=10)
        daily_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        for i, (param, var) in enumerate(self.daily_params.items()):
            ttk.Checkbutton(daily_frame, text=param.replace("_", " ").title(), variable=var).grid(row=i, column=0, sticky="w")

        # Weather Information Block
        weather_info_frame = ttk.LabelFrame(left_frame, text="Weather Information", padding=10)
        weather_info_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.weather_info_label = ttk.Label(weather_info_frame, text="", font=("Helvetica", 10))
        self.weather_info_label.grid(row=0, column=0, sticky="w")

        # Right Column
        right_frame = ttk.Frame(main_scrollable_frame)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Simulation Results Block
        results_frame = ttk.LabelFrame(right_frame, text="Simulation Results", padding=10)
        results_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.result_frame = ttk.Frame(results_frame)
        self.result_frame.grid(row=0, column=0, sticky="nsew")


    def load_locations(self):
        # Load locations from a CSV file
        try:
            with open("locations.csv", "r") as f:
                reader = csv.reader(f)
                locations = [row[0] for row in reader]
                locations.pop(0)
                self.location.set(locations[0]) 
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
            try:
                self.weather_data = response.json()
                self.weather_info = {
                    "latitude": self.weather_data["latitude"],
                    "longitude": self.weather_data["longitude"],
                    "timezone": self.weather_data["timezone"],
                    "elevation": self.weather_data["elevation"]
                }
                print("Weather data fetched successfully")
            except ValueError:
                print("Failed to parse weather data")
                self.weather_data = None
                self.weather_info = None
        else:
            print("Failed to fetch weather data")
            self.weather_data = None
            self.weather_info = None

    def run_simulations(self):
        self.result_label.config(text="Running simulations...")
        self.root.update_idletasks()


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
        # self.fetch_weather_data(latitude, longitude, params["start_date"], params["end_date"], params["hourly_params"], params["daily_params"])

        # self.display_weather_info()

        if self.weather_data:
            G, states, prob_general = generate_forest(GRID_SIZE, self.weather_data)
            params["prob_spread"] = prob_general
        else:
            G, states, prob_general = generate_forest(GRID_SIZE,None)
            params["prob_spread"] = self.prob_spread.get()

        # Ejecutar en paralelo
   

        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())  # Usa todos los núcleos disponibles
        # tasks = [(i,G,states,params["prob_spread"],params["num_iterations"]) for i in range(params["num_simulations"])]
        tasks = [(i,G,states,params,self.weather_data) for i in range(params["num_simulations"])]
        results = pool.starmap(execute_simulation, tasks)
        pool.close()
        pool.join()
        
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
        messagebox.showinfo("Success", "Simulations completed!")

    def get_location_coordinates(self, location_name):
        with open("locations.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == location_name:
                    return float(row[1]), float(row[2])
        return None, None


    def save_results(self, results, params):
        # Clear the existing results section
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # Display the parameters in three columns: General, Hourly, Daily
        ttk.Label(self.result_frame, text="Simulation Parameters", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=6, pady=10)

        # General Parameters
        ttk.Label(self.result_frame, text="General Parameters", font=("Helvetica", 10, "bold")).grid(row=1, column=0, columnspan=2, pady=5)
        general_params = ["num_simulations", "num_iterations", "prob_spread", "wind_direction", "wind_intensity", "num_obstacles", "start_date", "end_date", "location", "display_simulations", "auto_close_simulations", "custom_csv_name", "csv_name", "simulation_mode"]
        for i, key in enumerate(general_params):
            if key in params:
                ttk.Label(self.result_frame, text=f"{key.replace('_', ' ').title()}:").grid(row=2+i, column=0, sticky="e")
                ttk.Label(self.result_frame, text=f"{params[key]}").grid(row=2+i, column=1, sticky="w")

        # Hourly Parameters
        if params["simulation_mode"] == "hourly":
            ttk.Label(self.result_frame, text="Hourly Parameters", font=("Helvetica", 10, "bold")).grid(row=1, column=2, columnspan=2, pady=5)
            for i, (key, value) in enumerate(params["hourly_params"].items()):
                ttk.Label(self.result_frame, text=f"{key.replace('_', ' ').title()}:").grid(row=2+i, column=2, sticky="e")
                ttk.Label(self.result_frame, text=f"{value}").grid(row=2+i, column=3, sticky="w")

        # Daily Parameters
        if params["simulation_mode"] == "daily":
            ttk.Label(self.result_frame, text="Daily Parameters", font=("Helvetica", 10, "bold")).grid(row=1, column=4, columnspan=2, pady=5)
            for i, (key, value) in enumerate(params["daily_params"].items()):
                ttk.Label(self.result_frame, text=f"{key.replace('_', ' ').title()}:").grid(row=2+i, column=4, sticky="e")
                ttk.Label(self.result_frame, text=f"{value}").grid(row=2+i, column=5, sticky="w")

        # Display the results
        ttk.Label(self.result_frame, text="Simulation Results", font=("Helvetica", 12, "bold")).grid(row=len(general_params)+2, column=0, columnspan=6, pady=10)
        headers = ["Simulation", "Burnt Trees", "Iterations to Extinguish", "Max Fire Size"]
        for j, header in enumerate(headers):
            ttk.Label(self.result_frame, text=header, font=("Helvetica", 10, "bold")).grid(row=len(general_params)+3, column=j, padx=5, pady=5)

        for i, result in enumerate(results):
            for j, value in enumerate(result):
                ttk.Label(self.result_frame, text=value).grid(row=len(general_params)+4+i, column=j, padx=5, pady=5)

        # Determine the CSV file name
        if self.custom_csv_name.get():
            csv_file_name = params["csv_name"]
        else:
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            csv_file_name = f"results_{current_time}.csv"

        # Save the parameters and results to a CSV file
        with open(csv_file_name, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Parameter", "Value"])
            for key in general_params:
                if key in params:
                    writer.writerow([key, params[key]])
            writer.writerow([])  # Add an empty row for separation
            if params["simulation_mode"] == "hourly":
                writer.writerow(["Hourly Parameters"])
                for key, value in params["hourly_params"].items():
                    writer.writerow([key, value])
            elif params["simulation_mode"] == "daily":
                writer.writerow(["Daily Parameters"])
                for key, value in params["daily_params"].items():
                    writer.writerow([key, value])
            writer.writerow([])  # Add an empty row for separation
            writer.writerow(headers)
            writer.writerows(results)

        self.result_label.config(text="Simulations completed. Results saved in results.csv")
        messagebox.showinfo("Success", "Simulations result saved on the csv file!")

    def display_weather_info(self):
        if self.weather_info:
            info_text = (
                f"Latitude: {self.weather_info['latitude']}\n"
                f"Longitude: {self.weather_info['longitude']}\n"
                f"Timezone: {self.weather_info['timezone']}\n"
                f"Elevation: {self.weather_info['elevation']} meters"
            )
            self.weather_info_label.config(text=info_text)
        else:
            self.weather_info_label.config(text="No weather information available.")
if __name__ == "__main__":
    root = tk.Tk()
    app = FireSimulationApp(root)
    root.mainloop()