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