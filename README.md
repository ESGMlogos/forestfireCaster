# Forest Fire Simulation

This project simulates the spread of forest fires using various parameters and weather data from the Open-Meteo API.

## Installation

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Steps

1. **Clone the repository**:

    ```sh
    git clone https://github.com/yourusername/forestfireCaster.git
    cd forestfireCaster
    ```

2. **Create a virtual environment** (optional but recommended):

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:

    ```sh
    pip install -r requirements.txt
    ```

4. **Run the application**:

    ```sh
    python project/forestfireCaster/interface.py
    ```

## Usage

1. **Set the simulation parameters**:
    - Number of Simulations
    - Iterations per Simulation
    - Fire Spread Probability
    - Wind Direction
    - Wind Intensity
    - Number of Obstacles
    - Start Date
    - End Date
    - Location
    - Display Simulations
    - Simulations not to close automatically
    - Custom CSV Name
    - Simulation Mode (Hourly or Daily)
    - Hourly and Daily Weather Parameters

2. **Run the simulations**:
    - Click the "Run Simulations" button to start the simulations.

3. **View the results**:
    - The results will be displayed in the right column and saved to a CSV file.

## Adding Locations

1. **Add a new location**:
    - Enter the location name in the "Location" field.
    - Click the "Add Location" button to add the location to the [locations.csv](http://_vscodecontentref_/2) file.

## Fetching Weather Data

1. **Fetch weather data**:
    - The application will automatically fetch weather data based on the selected parameters and location.

## License

This project is licensed under the MIT License.