import json
from datetime import datetime

import requests
from decouple import config
from rich.console import Console

BASE_URL = "https://api.openweathermap.org/data/2.5/"
WEATHER_SERVICE = "{BASE_URL}weather?q={city_name}&appid={API_KEY}"
FORECAST_SERVICE = "{BASE_URL}forecast?lat={lat}&lon={lon}&appid={API_KEY}"
API_KEY = config("API_KEY")

WEATHER_DESCRIPTION = "d"
WEATHER_FORECAST = "f"
WEATHER_COMPARISON = "c"

console = Console()
current_day = datetime.now()
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
COMPARISON_LIST = []

city_list = []
checked_cities = []


def api_call(city_name: str):
    try:
        response = requests.get(
            WEATHER_SERVICE.format(
                BASE_URL=BASE_URL, city_name=city_name, API_KEY=API_KEY
            )
        ).json()
    except TimeoutError:
        console.print("[bold red]Unable to connect. Please try again later.[/]")

    if response["cod"] == "404":
        error_message = f"[bold red]{response['message'].capitalize()}[/]"
        console.print(error_message)
        return None

    console.print()
    add_to_checked_city_list(city_name.title())
    return response


def get_wind_direction(angle: int) -> None:
    if angle in ORDINARY_WIND_ANGLES:
        for direction, value in ORDINARY_WIND_DIRECTIONS.items():
            if angle == value:
                return direction + f" ({angle}°)"
    else:
        for direction, (min, max) in SPECIFIC_WIND_DIRECTIONS.items():
            if min < angle < max:
                return direction + f" ({angle}°)"


def get_weather_descriptions(response) -> dict:
    return {
        "weather_status": response["weather"][0]["main"],
        "weather_description": response["weather"][0]["description"].capitalize(),
        "temperature_celsius": response["main"]["temp"] - 273.15,
        "humidity": response["main"]["humidity"],
        "wind_speed": response["wind"]["speed"],
        "wind_direction": response["wind"]["deg"],
    }


def print_weather_descriptions(response, city_name: str, unit_preference: str) -> None:
    """Printing weather descriptions(weather, temperature and humidity)"""
    weather_descriptions = get_weather_descriptions(response)
    console.print()
    console.print(
        f"{city_name.title()} is {WEATHERS[weather_descriptions["weather_status"]]} today. ({weather_descriptions["weather_description"]})"
    )
    if unit_preference == "f" or unit_preference == "2":
        temperature_fahrenheit = (
            9 / 5 * float(weather_descriptions["temperature_celsius"]) + 32
        )
        console.print(f"Temperature: {temperature_fahrenheit:.2f}[bold cyan]°F[/]")
    else:
        console.print(
            f"Temperature: {weather_descriptions["temperature_celsius"]:.2f}[bold cyan]°C[/]"
        )
    console.print(f"Humidity: {weather_descriptions["humidity"]}[bold cyan]%[/]")
    console.print(
        f"Wind speed: [bold cyan]{weather_descriptions["wind_speed"]}m/s[/] (Direction: [bold cyan]{get_wind_direction(weather_descriptions["wind_direction"])}[/])"
    )
    console.input("[blue]Press enter to continue.[/]")
    console.print()


def get_unit_preference():
    console.print("Which unit system do you prefer")
    for index, unit in enumerate(UNITS, start=1):
        console.print(f"{index}. {unit}")
    return console.input().strip().lower()


def check_city_weather(city_name: str, response) -> None:
    unit_preference = get_unit_preference()
    console.print_weather_descriptions(response, city_name, unit_preference)
    console.rule()


def check_weather_forecast(response):
    forecast_response = requests.get(
        FORECAST_SERVICE.format(
            BASE_URL=BASE_URL,
            lat=response["coord"]["lat"],
            lon=response["coord"]["lon"],
            API_KEY=API_KEY,
        )
    ).json()
    console.print(forecast_response)


def weather_comparison(city_name: str, response):
    first_city_name = city_name
    first_city_info = get_weather_descriptions(response)
    while True:
        second_city_name = console.input(
            "Please input another city name: [bold red](q to quit)[/] "
        )
        if second_city_name == "q":
            break
        if second_city_name is not None:
            second_response = api_call(second_city_name)
            second_city_info = get_weather_descriptions(second_response)
            console.print("Which information do you want to compare?")
            # TODO: create the comparison list and print out a list for user to choose
            for index, (first_city_info, second_city_info) in enumerate(
                COMPARISON_LIST
            ):
                print(
                    f"{first_city_name},{first_city_info},{second_city_name},{second_city_info}"
                )


def function_select(city_name: str, response) -> None:
    """Select from functions"""
    function_choice = None
    while function_choice not in ("q", 4):
        console.print("Select a function:")
        for number, function in enumerate(FUNCTIONS, start=1):
            console.print(f"{number}. {function}")
            console.print()
        function_choice = input().strip().lower()[:1]
        console.print()
        console.rule()
        if function_choice in (1, WEATHER_DESCRIPTION):
            check_city_weather(city_name, response)
        elif function_choice in (2, WEATHER_FORECAST):
            check_weather_forecast(response)
        elif function_choice in (3, WEATHER_COMPARISON):
            weather_comparison(city_name, response)


def get_all_cities() -> None:
    """store all city name into a list"""
    with open("cities.json", "r", encoding="utf-8") as jsonfile:
        data = json.load(jsonfile)
    for city in data:
        city_list.append(city["name"])


def add_to_checked_city_list(city_name: str) -> None:
    """add new city name into checked city list"""
    if city_name not in checked_cities:
        checked_cities.append(city_name)


def main():
    console.print("Welcome to your weather dashboard.")
    console.print()
    while True:
        city_name = (
            console.input("Input a city name: [bold red](q to quit)[/] ")
            .strip()
            .lower()
        )
        if city_name == "q":
            break
        response = api_call(city_name)
        if response is not None:
            function_select(city_name, response)


if __name__ == "__main__":
    main()
