import math
from config import K
EMPTY, TREE, FIRE, ASH = 0, 1, 2, 3


def calculate_general_probability(weather_data):
    """
    Calculate the general probability of fire spread based on weather data.
    """
    # Example weights for each parameter (these can be adjusted)
    weights = {
        "temperature_2m": 0.3,
        "relative_humidity_2m": -0.2,
        "wind_speed_10m": 0.4,
        "soil_temperature_0_to_7cm": 0.1,
        "soil_temperature_7_to_28cm": 0.1
    }

    # Initialize probability
    probability = 0.0

    # Calculate weighted sum of parameters
    if "hourly" in weather_data:
        for param, weight in weights.items():
            if param in weather_data["hourly"]:
                # Use the average value of the parameter over the time period
                avg_value = sum(weather_data["hourly"][param]) / len(weather_data["hourly"][param])
                probability += weight * avg_value

    # Ensure probability is within [0, 1] range
    probability = max(0.0, min(1.0, probability))

    return probability
def calculate_specific_probability(weather_data, general_prob ,position, neighbors_states):
    """
    Calculate the specific probability of fire spread for a tree based on weather data and its position.
    """
    # Example weights for each parameter (these can be adjusted)
    weights = {
        "temperature_2m": 0.03,
        "relative_humidity_2m": -0.002,
        "wind_speed_10m": 0.2,
        "soil_temperature_0_to_7cm": 0.01,
        "soil_temperature_7_to_28cm": 0.01,
        "temperature_2m_max": 0.02,
        "temperature_2m_min": 0.01,
        "temperature_2m_mean": 0.02,
        "wind_speed_10m_max": 0.03,
        "wind_gusts_10m_max": 0.03,
        "wind_direction_10m_dominant": 0.02,
        "shortwave_radiation_sum": 0.01,
        "et0_fao_evapotranspiration": 0.01
    }
    print(f"")
    print(f"----------------------------------------------------------------")
    print(f"")
    # Initialize probability
    probability = general_prob
    
    print(f"weather data: {weather_data}, Position: {position}, neighbors: {neighbors_states}")

    windVector = getWindVector(weather_data, position, neighbors_states)
    weather_data["wind_speed_10m"] = windVector

    weighted_sum = 0
    # Calculate weighted sum of parameters for the specific position
    for param, weight in weights.items():
        if param in weather_data and weather_data[param] is not None:
            # Use the value of the parameter at the specific position
            value = weather_data[param]
            weighted_sum += weight * value
            print(f"Param: {param}, Weight: {weight}, Value: {value}, calculatedWeight: {weight * value}, Weighted Sum: {weighted_sum}")

    print(f"Initial Probability: {probability}")
    print(f"Weighted Sum: {weighted_sum}")


    # alpha = 0.2  # Controls how steep the sigmoid curve is
    # probability += sigmoid(weighted_sum, alpha)
    k = K
    probability += weighted_sum
    print(f"Probability after adding weighted sum: {probability}")


    probability = 0 if probability < 0 else probability
    probability = probability / (probability + k)
    # Ensure probability is within [0, 1] range
    probability = max(0.0, min(1.0, probability))
    print(f"Final Probability: {probability}")
    print(f"")
    print(f"----------------------------------------------------------------")
    print(f"")

    return probability


def sigmoid(x, alpha=0.1):
    """Sigmoid function for smooth probability scaling."""
    return 1 / (1 + math.exp(-alpha * x))

def calculate_ranges_spread_probabilities(prob_spread_ini, prob_spread_fin, prob_spread_step):
    step_value = (prob_spread_fin - prob_spread_ini) / (prob_spread_step)
    probabilities = []

    current_value = prob_spread_ini
    while current_value <= prob_spread_fin:
        probabilities.append(current_value)
        current_value += step_value

    return probabilities

def getWindVector(weather_data, position, neighbors_states):
    """
    Calculate the wind vector based on wind speed and direction.
    """
    wind_speed = weather_data["wind_speed_10m"]
    wind_direction = weather_data["wind_direction_10m"]

    wind_vectors = []
    for neighbor, state in neighbors_states.items():
        if state == FIRE:
            neighbor_position = getNeighborPosition(position, neighbor)
            print(f"NeigborPosition: {neighbor_position}")

            grades = (neighbor_position) + wind_direction
            print(f"NeigborPosition in grades: {grades}")

            wind_direction_rad = math.radians(grades)
            print(f"NeigborPosition in radians: {wind_direction_rad}")

            
            wind_vectors.append(wind_speed * math.cos(wind_direction_rad))             

    
    print(f"This is the  vectors: {wind_vectors}")
    wind_vector = sum(wind_vectors)
    print(f"This is the final vector: {wind_vector}")

    return wind_vector

def getNeighborPosition(position,nieghbor):
    position_x, position_y = position
    neighbor_x, neighbor_y = nieghbor

    if position_x + 1 == neighbor_x and position_y == neighbor_y:
        return 0
    elif position_x - 1 == neighbor_x and position_y == neighbor_y:
        return 180
    elif position_x == neighbor_x and position_y + 1 == neighbor_y:
        return 90
    elif position_x == neighbor_x and position_y - 1 == neighbor_y:
        return 270
