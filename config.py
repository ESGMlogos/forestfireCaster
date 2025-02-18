
# Sise of the Forest
GRID_SIZE = (9, 9)

# Fire spread Factors
BASE_SPREAD_PROB = 0.3
WIND_EFFECT = {
    "N": 1.2,  
    "S": 0.8,
    "E": 1.1,
    "W": 0.9
}
SOIL_TYPE_EFFECT = {
    "dry": 1.5,
    "normal": 1.0,
    "wet": 0.5
}
GARBAGE_INTENSITY = {
    "none": 1.0,
    "low": 1.2,
    "high": 1.5
}

# The fire shall start in more than one place, by now this is a constant. 
INITIAL_FIRE_POINTS = 3
