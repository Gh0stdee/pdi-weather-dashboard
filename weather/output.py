WEATHER_DESCRIPTION = "d"
WEATHER_FORECAST = "f"
WEATHER_COMPARISON = "c"

FUNCTIONS = [
    "Weather Description [bold blue](d)[/]",
    "Weather Forecast [bold blue](f)[/]",
    "Weather Comparison [bold blue](c)[/]",
    "Check Another City [bold red](q)[/]",
]

UNITS = ["Degree Celcius °C [bold blue](default)[/]", "Fahrenheit °F [bold blue](f)[/]"]
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

# COMPARISON_LIST = []
