from collections import Counter
from datetime import datetime, timedelta
from difflib import get_close_matches
from enum import StrEnum

CURRENT_DAY = datetime.now()
FIVE_DAYS = 5
DATE_INDEX = 10
INVALID_WIND_DIRECTION = "(Invalid wind direction)"

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


class UnitType(StrEnum):
    CELSIUS = "c"
    FAHRENHEIT = "f"


class Comparison_Feature(StrEnum):
    ALL = "a"
    WEATHER = "w"
    TEMPERATURE = "t"


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
    return INVALID_WIND_DIRECTION


def get_weather_descriptions(response) -> dict:
    """Return a tidy information dictionary from the response"""
    return {
        "weather_status": response["weather"][0]["main"],
        "weather_description": response["weather"][0]["description"].capitalize(),
        "temperature_celsius": from_kelvin_convert_to_celsius(response["main"]["temp"]),
        "humidity": response["main"]["humidity"],
        "wind_speed": response["wind"]["speed"],
        "wind_direction": response["wind"]["deg"],
    }


def get_all_cities() -> list[str]:
    """Store all city name into a list"""
    city_list = []
    with open("cities2.txt", "r", encoding="utf-8") as file:
        for city_name in file:
            city_list.append(city_name.rstrip())
    return city_list


def fuzzy_search(city: str) -> None | str:
    """Return a list of city names that is close to search input"""
    new_search = get_close_matches(city, get_all_cities())
    if len(new_search) < 1:
        return None
    else:
        return new_search


def get_five_days_for_forecast():
    five_days_list = []
    for i in range(0, FIVE_DAYS):
        five_days_list.append(str(CURRENT_DAY + timedelta(days=i))[:DATE_INDEX])
    return five_days_list


def parse_forecast_response(forecast_response, five_days_list):
    first_day_temperature = []
    first_day_forecast_weather_count = Counter()
    second_day_temperature = []
    second_day_forecast_weather_count = Counter()
    third_day_temperature = []
    third_day_forecast_weather_count = Counter()
    fourth_day_temperature = []
    fourth_day_forecast_weather_count = Counter()
    fifth_day_temperature = []
    fifth_day_forecast_weather_count = Counter()
    temperature_and_weather_forecast = []
    for forecast_info in forecast_response["list"]:
        if forecast_info["dt_txt"][:DATE_INDEX] == five_days_list[0]:
            first_day_forecast_weather_count.update(
                [forecast_info["weather"][0]["main"]]
            )
            first_day_temperature.append(forecast_info["main"]["temp"])
        elif forecast_info["dt_txt"][:DATE_INDEX] == five_days_list[1]:
            second_day_forecast_weather_count.update(
                [forecast_info["weather"][0]["main"]]
            )
            second_day_temperature.append(forecast_info["main"]["temp"])
        elif forecast_info["dt_txt"][:DATE_INDEX] == five_days_list[2]:
            third_day_forecast_weather_count.update(
                [forecast_info["weather"][0]["main"]]
            )
            third_day_temperature.append(forecast_info["main"]["temp"])
        elif forecast_info["dt_txt"][:DATE_INDEX] == five_days_list[3]:
            fourth_day_forecast_weather_count.update(
                [forecast_info["weather"][0]["main"]]
            )
            fourth_day_temperature.append(forecast_info["main"]["temp"])
        elif forecast_info["dt_txt"][:DATE_INDEX] == five_days_list[4]:
            fifth_day_forecast_weather_count.update(
                [forecast_info["weather"][0]["main"]]
            )
            fifth_day_temperature.append(forecast_info["main"]["temp"])
    temperature_and_weather_forecast.append(
        (first_day_temperature, first_day_forecast_weather_count)
    )
    temperature_and_weather_forecast.append(
        (second_day_temperature, second_day_forecast_weather_count)
    )
    temperature_and_weather_forecast.append(
        (third_day_temperature, third_day_forecast_weather_count)
    )
    temperature_and_weather_forecast.append(
        (fourth_day_temperature, fourth_day_forecast_weather_count)
    )
    temperature_and_weather_forecast.append(
        (fifth_day_temperature, fifth_day_forecast_weather_count)
    )

    return temperature_and_weather_forecast
