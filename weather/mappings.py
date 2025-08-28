from difflib import get_close_matches

"""API Weather Response Mapping"""
WEATHERS = {
    "Clear": "sunny",
    "Clouds": "cloudy",
    "Drizzle": "drizzly",
    "Rain": "rainy",
    "Thunderstorm": "stormy",
    "Snow": "snowy",
    "Mist": "misty",
    "Smoke": "smokey",
    "Haze": "hazy",
    "Dust": "dusty",
    "Fog": "foggy",
    "Sand": "sandy",
    "Ash": "ashy",
    "Squall": "squally",
    "Tornado": "being hit with a tornado",
}

ORDINARY_WIND_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]

ORDINARY_WIND_DIRECTIONS = {
    "N": ORDINARY_WIND_ANGLES[0],
    "NE": ORDINARY_WIND_ANGLES[1],
    "E": ORDINARY_WIND_ANGLES[2],
    "SE": ORDINARY_WIND_ANGLES[3],
    "S": ORDINARY_WIND_ANGLES[4],
    "SW": ORDINARY_WIND_ANGLES[5],
    "W": ORDINARY_WIND_ANGLES[6],
    "NW": ORDINARY_WIND_ANGLES[7],
}

SPECIFIC_WIND_DIRECTIONS = {
    "NNE": (0, 45),
    "ENE": (45, 90),
    "ESE": (90, 135),
    "SSE": (135, 180),
    "SSW": (180, 225),
    "WSW": (225, 270),
    "WNW": (270, 315),
    "NNW": (315, 360),
}


def from_kelvin_convert_to_celsius(temperature: float) -> float:
    return temperature - 273.15


def from_celsius_convert_to_fahrenheit(temperature: float) -> float:
    return temperature * 9 / 5 + 32


def get_wind_direction(angle: int) -> str:
    """Return wind direction using the angle response"""
    if angle in ORDINARY_WIND_ANGLES:
        for direction, value in ORDINARY_WIND_DIRECTIONS.items():
            if angle == value:
                return direction + f" ({angle}°)"
    else:
        for direction, (min, max) in SPECIFIC_WIND_DIRECTIONS.items():
            if min < angle < max:
                return direction + f" ({angle}°)"
    return "(Invalid wind direction)"


def get_all_cities() -> list[str]:
    """Store all city name into a list"""
    city_list = []
    with open("cities2.txt", "r", encoding="utf-8") as file:
        for city_name in file:
            city_list.append(city_name.rstrip())
    return city_list


def fuzzy_search(city: str) -> None | str:
    """Find a city name close to the searched name"""
    new_search = get_close_matches(city, get_all_cities())
    if len(new_search) < 1:
        return None
    else:
        return new_search
