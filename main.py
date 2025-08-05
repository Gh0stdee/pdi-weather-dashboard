import json
from collections import Counter
from datetime import datetime, timedelta

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
CURRENT_DAY = datetime.now()
six_days_list = []
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
COMPARISON_LIST = ["Weather", "Temperature"]
WEATHER = "1"
TEMPERATURE = "2"

city_list = []
checked_cities = []


def from_kelvin_convert_to_celsius(temperature: float) -> float:
    return temperature - 273.15


def from_celsius_convert_to_fahrenheit(temperature: float) -> float:
    return temperature * 9 / 5 + 32


def api_call(city_name: str):
    try:
        response = requests.get(
            WEATHER_SERVICE.format(
                BASE_URL=BASE_URL, city_name=city_name, API_KEY=API_KEY
            )
        ).json()
    except requests.exceptions.ConnectTimeout:
        console.print("[bold red]Unable to connect. Please try again later.[/]")
        return None

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
        "temperature_celsius": from_kelvin_convert_to_celsius(response["main"]["temp"]),
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
    if unit_preference in ("2", "f"):
        temperature_fahrenheit = from_celsius_convert_to_fahrenheit(
            float(weather_descriptions["temperature_celsius"])
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


def get_unit_preference() -> str:
    """Ask user for unit preference: f: fahrenheit anything else: celsius"""
    console.print("Which unit system do you prefer")
    for index, unit in enumerate(UNITS, start=1):
        console.print(f"{index}. {unit}")
    return console.input().strip().lower()


def check_city_weather(city_name: str, response) -> None:
    unit_preference = get_unit_preference()
    print_weather_descriptions(response, city_name, unit_preference)
    console.rule()


def get_six_days_for_forecast():
    for i in range(0, 6):
        six_days_list.append(str(CURRENT_DAY + timedelta(days=i))[:10])


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
sixth_day_temperature = []
sixth_day_forecast_weather_count = Counter()
temperature_and_weather_forecast = []


def check_weather_forecast(response):
    forecast_response = requests.get(
        FORECAST_SERVICE.format(
            BASE_URL=BASE_URL,
            lat=response["coord"]["lat"],
            lon=response["coord"]["lon"],
            API_KEY=API_KEY,
        )
    ).json()
    get_six_days_for_forecast()
    for forecast_info in forecast_response["list"]:
        if forecast_info["dt_txt"][:10] == six_days_list[0]:
            first_day_forecast_weather_count.update(
                [forecast_info["weather"][0]["main"]]
            )
            first_day_temperature.append(forecast_info["main"]["temp"])
        elif forecast_info["dt_txt"][:10] == six_days_list[1]:
            second_day_forecast_weather_count.update(
                [forecast_info["weather"][0]["main"]]
            )
            second_day_temperature.append(forecast_info["main"]["temp"])
        elif forecast_info["dt_txt"][:10] == six_days_list[2]:
            third_day_forecast_weather_count.update(
                [forecast_info["weather"][0]["main"]]
            )
            third_day_temperature.append(forecast_info["main"]["temp"])
        elif forecast_info["dt_txt"][:10] == six_days_list[3]:
            fourth_day_forecast_weather_count.update(
                [forecast_info["weather"][0]["main"]]
            )
            fourth_day_temperature.append(forecast_info["main"]["temp"])
        elif forecast_info["dt_txt"][:10] == six_days_list[4]:
            fifth_day_forecast_weather_count.update(
                [forecast_info["weather"][0]["main"]]
            )
            fifth_day_temperature.append(forecast_info["main"]["temp"])
        elif forecast_info["dt_txt"][:10] == six_days_list[5]:
            sixth_day_forecast_weather_count.update(
                [forecast_info["weather"][0]["main"]]
            )
            sixth_day_temperature.append(forecast_info["main"]["temp"])
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
    temperature_and_weather_forecast.append(
        (sixth_day_temperature, sixth_day_forecast_weather_count)
    )

    unit_preference = get_unit_preference()
    console.print()
    for day_index, (temperatures_of_the_day, weather_counts_of_the_day) in enumerate(
        temperature_and_weather_forecast
    ):
        console.print(f"[{six_days_list[day_index]}]")
        if weather_counts_of_the_day.most_common(1)[0] == "Tornado":
            console.print(
                "[bold red]The city is likely to be hit by a tornado! Please stay safe![/]"
            )
        else:
            console.print(
                f"The weather on this day is mostly {WEATHERS[weather_counts_of_the_day.most_common(1)[0][0]]}."
            )
        average_temperature = from_kelvin_convert_to_celsius(
            sum(temperatures_of_the_day) / len(temperatures_of_the_day)
        )
        if unit_preference in ("2", "f"):
            unit = "°F"
            average_temperature = from_celsius_convert_to_fahrenheit(
                average_temperature
            )
        else:
            unit = "°C"
        console.print(
            f"The average temperature will be {average_temperature:.2f}{unit}."
        )
        console.print()
    console.input("[blue]Press enter to continue.[/]")
    console.print()
    console.rule()


def weather_comparison(city_name: str, response):
    first_city_name = city_name.title()
    first_city_info = get_weather_descriptions(response)
    while True:
        second_city_name = console.input(
            "Please input another city name for comparison: [bold red](q to quit)[/]\n"
        ).title()
        if second_city_name == "Q":
            break

        second_response = api_call(second_city_name)
        if second_response is not None:
            add_to_checked_city_list(second_city_name)
            while True:
                second_city_info = get_weather_descriptions(second_response)
                console.print("Which information do you want to compare?")
                # TODO: create the comparison list and print out a list for user to choose
                for index, info_to_compare in enumerate(COMPARISON_LIST, start=1):
                    console.print(f"{index}. {info_to_compare}")
                info = console.input().strip()
                if info == WEATHER:
                    console.print(
                        f"{first_city_name} is {WEATHERS[first_city_info["weather_status"]]}, while {second_city_name} is {WEATHERS[second_city_info["weather_status"]]}."
                    )
                    break
                elif info == TEMPERATURE:
                    console.print()
                    unit_preference = get_unit_preference()
                    console.print()
                    first_city_temp = first_city_info["temperature_celsius"]
                    second_city_temp = second_city_info["temperature_celsius"]
                    difference = first_city_temp - second_city_temp
                    if unit_preference in ("2", "f"):
                        difference *= 9 / 5
                        unit = "°F"
                    else:
                        unit = "°C"
                    if difference < 0:
                        console.print(
                            f"{first_city_name} is {abs(difference):.2f} {unit} colder than {second_city_name}."
                        )
                    elif difference > 0:
                        console.print(
                            f"{first_city_name} is {difference:.2f} {unit} colder than {second_city_name}."
                        )
                    else:
                        console.print(
                            f"{first_city_name} has the same temperaure as {second_city_name}."
                        )
                    break
                else:
                    console.print("[bold red]Invalid input.[/]")
        console.input("[blue]Press enter to continue.[/]")
        console.print()
        console.rule()
        break


def function_select(city_name: str, response) -> None:
    """Select from functions"""
    function_choice = None
    while function_choice not in ("q", "4"):
        console.print("Select a function:")
        for number, function in enumerate(FUNCTIONS, start=1):
            console.print(f"{number}. {function}")
            console.print()
        function_choice = input().strip().lower()
        console.print()
        console.rule()
        if function_choice in ("1", WEATHER_DESCRIPTION):
            check_city_weather(city_name, response)
        elif function_choice in ("2", WEATHER_FORECAST):
            check_weather_forecast(response)
        elif function_choice in ("3", WEATHER_COMPARISON):
            weather_comparison(city_name, response)


def get_all_cities() -> None:
    """store all city name into a list"""
    with open(".cities.json", "r", encoding="utf-8") as jsonfile:
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
    get_six_days_for_forecast()
    print(six_days_list)
    main()
