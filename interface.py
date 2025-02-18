import matplotlib.pyplot as plt
import matplotlib.animation as animation
import tkinter as tk
import random
import networkx as nx
from tkinter import ttk, messagebox
import multiprocessing
import csv
import requests
from run_simulations import execute_simulation
from environment import generate_forest
from simulation import save_simulation
from simulation import visualize_simulation
from config import GRID_SIZE
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import csv

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
        self.start_date = tk.StringVar(value=(datetime.now() - relativedelta(years=33)).strftime("%Y-%m-%d"))
        self.end_date = tk.StringVar(value=(datetime.now() - relativedelta(years=33) + timedelta(days=9)).strftime("%Y-%m-%d"))
        self.location = tk.StringVar()
        self.display_simulations = tk.BooleanVar(value=True)
        self.auto_close_simulations = tk.BooleanVar(value=True)
        self.custom_csv_name = tk.BooleanVar(value=False)
        self.csv_name = tk.StringVar(value="results.csv")
        self.use_api_data = tk.BooleanVar(value=True)
        self.overtime = tk.BooleanVar(value=False)
        self.random_fire_start = tk.BooleanVar(value=False)
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

        ini_row, ini_col = GRID_SIZE
        self.forest_rows = tk.IntVar(value=ini_row)
        self.forest_columns = tk.IntVar(value=ini_col)


        self.num_fire_points = tk.IntVar(value=2)
        self.fire_points_rows = [tk.IntVar(value=1),tk.IntVar(value=2),tk.IntVar(value=3),tk.IntVar(value=4),tk.IntVar(value=5)]
        self.fire_points_cols = [tk.IntVar(value=1),tk.IntVar(value=2),tk.IntVar(value=3),tk.IntVar(value=4),tk.IntVar(value=5)]

        self.new_location_name = tk.StringVar(value="")
        self.new_location_latitude = tk.StringVar(value="")
        self.new_location_longitude = tk.StringVar(value="")

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
        self.simulations_entry = ttk.Entry(input_frame, textvariable=self.num_simulations)
        self.simulations_entry.grid(row=0, column=1, sticky="ew")

        ttk.Label(input_frame, text="Iterations per Simulation:").grid(row=0, column=2, sticky="w")
        self.iterations_entry = ttk.Entry(input_frame, textvariable=self.num_iterations)
        self.iterations_entry.grid(row=0, column=3, sticky="ew")

        ttk.Label(input_frame, text="Fire Spread Probability:").grid(row=2, column=0, sticky="w")
        self.spread_prob_entry = ttk.Entry(input_frame, textvariable=self.prob_spread)
        self.spread_prob_entry.grid(row=2, column=1, sticky="ew")

        ttk.Label(input_frame, text="Number of Obstacles:").grid(row=4, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.num_obstacles).grid(row=4, column=1, sticky="ew")

        ttk.Label(input_frame, text="Start Date:").grid(row=5, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.start_date).grid(row=5, column=1, sticky="ew")

        ttk.Label(input_frame, text="End Date:").grid(row=5, column=0 + 2, sticky="w")
        ttk.Entry(input_frame, textvariable=self.end_date).grid(row=5, column=1 + 2, sticky="ew")

        ttk.Label(input_frame, text="Location:").grid(row=6, column=0, sticky="w")
        self.location_combobox = ttk.Combobox(input_frame, textvariable=self.location)
        self.location_combobox.grid(row=6, column=1, pady=3, sticky="ew")
        self.load_locations()

        ttk.Button(input_frame, text="Add Location", command=self.show_add_location_fields).grid(row=6, column=2, columnspan=2, sticky="ew")

        # Row 7: Labels for name, latitude, longitude, and save button
        self.name_label = ttk.Label(input_frame, text="Name:")
        self.latitude_label = ttk.Label(input_frame, text="Latitude:")
        self.longitude_label = ttk.Label(input_frame, text="Longitude:")
        self.save_button = ttk.Button(input_frame, text="Save", command=self.add_location)

        # Row 8: Input fields for name, latitude, and longitude
        self.name_entry = ttk.Entry(input_frame, textvariable=self.new_location_name)
        self.latitude_entry = ttk.Entry(input_frame, textvariable=self.new_location_latitude)
        self.longitude_entry = ttk.Entry(input_frame, textvariable=self.new_location_longitude)

        self.hide_add_location_fields()    

        ttk.Label(input_frame, text="Forest Size:").grid(row=9, column=0, pady=1, columnspan=4, sticky="w")
        ttk.Label(input_frame, text="Rows:").grid(row=10, column=0, sticky="w")
        self.forest_rows_entry = ttk.Entry(input_frame, textvariable=self.forest_rows)
        self.forest_rows_entry.grid(row=10, column=1, sticky="ew")

        ttk.Label(input_frame, text="Columns:").grid(row=10, column=2, sticky="w")
        self.forest_columns_entry = ttk.Entry(input_frame, textvariable=self.forest_columns)
        self.forest_columns_entry.grid(row=10, column=3, sticky="ew")


        # Number of Fire Starting Points
        ttk.Label(input_frame, text="").grid(row=11, column=0, sticky="w")
        ttk.Label(input_frame, text="Number of Fire Starting Points:").grid(row=12, column=0, sticky="w")
        self.num_fire_points_combobox = ttk.Combobox(input_frame, textvariable=self.num_fire_points, values=[1, 2, 3, 4, 5])
        self.num_fire_points_combobox.grid(row=12, column=1, columnspan=2,sticky="ew")
        self.num_fire_points_combobox.bind("<<ComboboxSelected>>", self.update_fire_points_entries)

        # Fire Starting Points Entries (initially hidden)
        self.fire_points_entries = []
        for i in range(5):
            initial_row = random.randint(0, self.forest_rows.get() - 1)
            initial_col = random.randint(0, self.forest_columns.get() - 1)
            self.fire_points_rows[i].set(initial_row)
            self.fire_points_cols[i].set(initial_col)

            label = ttk.Label(input_frame, text=f"Fire Point {i+1} :")
            row_entry = ttk.Entry(input_frame, textvariable=self.fire_points_rows[i])
            col_entry = ttk.Entry(input_frame, textvariable=self.fire_points_cols[i])
            self.fire_points_entries.append((label, row_entry, col_entry))
        

        ttk.Checkbutton(input_frame, text="Display Simulations", variable=self.display_simulations).grid(row=21, column=2, columnspan=2, sticky="w")
        ttk.Checkbutton(input_frame, text="Simulations not to close automatically", variable=self.auto_close_simulations).grid(row=21, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(input_frame, text="Custom CSV Name", variable=self.custom_csv_name, command=self.toggle_csv_name_entry).grid(row=19, column=0, columnspan=2, sticky="w")
        self.csv_name_entry = ttk.Entry(input_frame, textvariable=self.csv_name, state="disabled")
        self.csv_name_entry.grid(row=19, column=1, columnspan=2, sticky="ew")

        
        ttk.Checkbutton(input_frame, text="Use API Data Simulation", variable=self.use_api_data, command=self.toggle_spread_prob_entry).grid(row=20, column=0, columnspan=2, sticky="w")

        
        ttk.Checkbutton(input_frame, text="Over the time", variable=self.overtime, command=self.toggle_iterations_entry).grid(row=20, column=2, columnspan=2, sticky="w")

        
        ttk.Checkbutton(input_frame, text="Randomized Fire Starting Point", variable=self.random_fire_start, command=self.toggle_fire_points_entries).grid(row=18, column=0, columnspan=2, pady=5, sticky="w")

        ttk.Label(input_frame, text="Simulation Mode:").grid(row=23, column=0, sticky="w")
        ttk.Radiobutton(input_frame, text="Hourly", variable=self.simulation_mode, value="hourly").grid(row=23, column=1, sticky="w")
        ttk.Radiobutton(input_frame, text="Daily", variable=self.simulation_mode, value="daily").grid(row=23, column=2, sticky="w")
            
        
        ttk.Button(left_frame, text="Run Simulations", command=self.run_simulations).grid(row=1, column=0, pady=10, sticky="ew")
        

        self.update_fire_points_entries(self)

        

        
        
        
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


        # Right Column
        right_frame = ttk.Frame(main_scrollable_frame)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Weather Information Block
        weather_info_frame = ttk.LabelFrame(right_frame, text="Weather Information", padding=10)
        weather_info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.weather_info_label = ttk.Label(weather_info_frame, text="", font=("Helvetica", 10))
        self.weather_info_label.grid(row=0, column=0, sticky="w")

        # Simulation Results Block
        results_frame = ttk.LabelFrame(right_frame, text="Simulation Results", padding=10)
        results_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.result_frame = ttk.Frame(results_frame)
        self.result_frame.grid(row=0, column=0, sticky="nsew")


    def toggle_fire_points_entries(self):
        if self.random_fire_start.get():
            state="disabled"
        else:
            state="normal"

        for widgets in self.fire_points_entries:
            for widget in widgets:
                widget.config(state=state)

    def update_fire_points_entries(self, event):
        if not self.random_fire_start.get():
            for widgets in self.fire_points_entries:
                for widget in widgets:
                    widget.grid_remove()

            num_points = int(self.num_fire_points.get())
            for i in range(num_points):
                self.fire_points_entries[i][0].grid(row=13 + i, column=0, sticky="w")
                self.fire_points_entries[i][1].grid(row=13 + i, column=1, sticky="ew")
                self.fire_points_entries[i][2].grid(row=13 + i, column=2, sticky="w")


    def toggle_iterations_entry(self):
        if self.overtime.get():
            self.iterations_entry.config(state="disabled")
        else:
            self.iterations_entry.config(state="normal")

    def toggle_spread_prob_entry(self):
        if self.use_api_data.get():
            self.spread_prob_entry.config(state="disabled")
        else:
            self.spread_prob_entry.config(state="normal")

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

    def show_add_location_fields(self):
        self.name_label.grid(row=7, column=0, sticky="w")
        self.latitude_label.grid(row=7, column=1, sticky="w")
        self.longitude_label.grid(row=7, column=2, sticky="w")

        self.name_entry.grid(row=8, column=0, sticky="ew")
        self.latitude_entry.grid(row=8, column=1, sticky="ew")
        self.longitude_entry.grid(row=8, column=2, sticky="ew")
        self.save_button.grid(row=8, column=3, sticky="ew")

    def hide_add_location_fields(self):
        self.name_label.grid_remove()
        self.latitude_label.grid_remove()
        self.longitude_label.grid_remove()
        self.save_button.grid_remove()

        self.name_entry.grid_remove()
        self.latitude_entry.grid_remove()
        self.longitude_entry.grid_remove()

    def add_location(self):
        # Add a new location to the CSV file
        new_location_name = self.new_location_name.get()
        new_location_latitude = self.new_location_latitude.get()
        new_location_longitude = self.new_location_longitude.get()

        if new_location_name and new_location_latitude and new_location_longitude:
            with open("locations.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([new_location_name, new_location_latitude, new_location_longitude])
            self.load_locations()
            self.hide_add_location_fields()

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
            "daily_params": {k: v.get() for k, v in self.daily_params.items()},
            "use_api_data": self.use_api_data.get(),
            "overtime": self.overtime.get(),
            "random_fire_start": self.random_fire_start.get(),
            "forest_rows": self.forest_rows.get(),
            "forest_columns": self.forest_columns.get(),
            "num_fire_points": self.num_fire_points.get(),
            "fire_points": [(self.fire_points_rows[i].get(), self.fire_points_cols[i].get()) for i in range(self.num_fire_points.get())]
        }

        # Fetch weather data
        self.weather_data = None
        location = self.location.get()
        latitude, longitude = self.get_location_coordinates(location)
        if params["use_api_data"]:
            self.fetch_weather_data(latitude, longitude, params["start_date"], params["end_date"], params["hourly_params"], params["daily_params"])        
        self.display_weather_info()

        forestWheater = self.weather_data
        forestSize = (params["forest_rows"], params["forest_columns"]) 
        G, states, prob_general = generate_forest(forestSize, forestWheater,params)

        if forestWheater:
            # params["prob_spread"] = prob_general
            params["prob_spread"] = self.prob_spread.get()

        # Ejecutar en paralelo
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())  # Usa todos los núcleos disponibles
        tasks = [(i,G,states,params,self.weather_data) for i in range(params["num_simulations"])]
        results = pool.starmap(execute_simulation, tasks)
        pool.close()
        pool.join()
        
        # Create directories for results
        # Determine the CSV file name
        if not self.custom_csv_name.get():
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            params["csv_name"] = f"results_{current_time}"

        csv_folder = "CSVs"
        simulation_folder = os.path.join(csv_folder, params["csv_name"])
        last_iteration_folder = os.path.join(simulation_folder, "LastIteration")
        image_folder = os.path.join(simulation_folder, "Image")

        os.makedirs(last_iteration_folder, exist_ok=True)
        os.makedirs(image_folder, exist_ok=True)

        # Guardar resultados
        # analitycs = getAnalysisFromResults(results)
        # Save results
        self.display_results(results, params)
        self.save_results(results, params, last_iteration_folder, image_folder,G)

        self.result_label.config(text="Simulations completed. Results saved in results.csv")
        messagebox.showinfo("Success", "Simulations completed!")

    def get_location_coordinates(self, location_name):
        with open("locations.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == location_name:
                    return float(row[1]), float(row[2])
        return None, None


    def save_results(self, results, params, last_iteration_folder, image_folder,forest):

        general_params = ["num_simulations", "num_iterations", "prob_spread", "wind_direction", "wind_intensity", "num_obstacles", "start_date", "end_date", "location", "display_simulations", "auto_close_simulations", "custom_csv_name", "csv_name", "simulation_mode"]
        headers = ["Simulation", "Burnt Trees", "Iterations to Extinguish", "Max Fire Size"]

        for result in results:
            output, final_forest = result["results"], result["Finalforest"]
            simulation_id = output[0]        
            # Save final iteration
            final_iteration_file = os.path.join(last_iteration_folder, f"final_iteration_{simulation_id}.csv")
            with open(final_iteration_file, "w", newline="") as f:
                writer = csv.writer(f)
                for row in final_forest:
                    writer.writerow(row)

            # Save image of the last simulation
            image_file = os.path.join(image_folder, f"simulation_{simulation_id}.png")
            save_simulation([final_forest], forest, simulation_id, save_path=image_file)

        
        csv_file_name = params["csv_name"] + ".csv"
        results_file = os.path.join("CSVs", params["csv_name"], csv_file_name)
        # Save the parameters and results to a CSV file
        with open(results_file, "w", newline="") as f:
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


    def display_results(self,results, params):
                # Clear the existing results section
        data = []
        for result in results:
            data.append(result)

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