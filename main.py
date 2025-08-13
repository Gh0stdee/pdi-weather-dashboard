from collections import Counter
from datetime import datetime, timedelta
from enum import StrEnum

import requests
import requests_cache
import typer
from decouple import config
from rich.console import Console

app = typer.Typer()

response = None
API_KEY = config("API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/"
WEATHER_SERVICE = (
    f"{BASE_URL}weather?appid={API_KEY}" + "&q={city_name}&appid={API_KEY}"
)
FORECAST_SERVICE = f"{BASE_URL}forecast?appid={API_KEY}" + "&lat={lat}&lon={lon}"
ONE_DAY = 86400
requests_cache.install_cache("cache.db", backend="sqlite", expire_after=ONE_DAY)


class Dashboard_Functions(StrEnum):
    WEATHER_DETAILS = "d"
    WEATHER_FORECAST = "f"
    WEATHER_COMPARISON = "c"


class UnitType(StrEnum):
    CELSIUS = "c"
    FAHRENHEIT = "f"


class Comparison_Features(StrEnum):
    ALL = "a"
    WEATHER = "w"
    TEMPERATURE = "t"


console = Console()
CURRENT_DAY = datetime.now()

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

ORDINARY_WIND_ANGLES: list[int] = [0, 45, 90, 135, 180, 225, 270, 315]

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

SPECIFIC_WIND_DIRECTIONS: dict = {
    "NNE": (0, 45),
    "ENE": (45, 90),
    "ESE": (90, 135),
    "SSE": (135, 180),
    "SSW": (180, 225),
    "WSW": (225, 270),
    "WNW": (270, 315),
    "NNW": (315, 360),
}
COMPARISON_LIST: list[str] = ["Weather [blue](w)[/]", "Temperature [blue](t)[/]"]

"""list of all cities"""
city_list = []


def from_kelvin_convert_to_celsius(temperature: float) -> float:
    return temperature - 273.15


def from_celsius_convert_to_fahrenheit(temperature: float) -> float:
    return temperature * 9 / 5 + 32


def call_api(city_name: str, compare: bool = False):
    # if !(response.from_cache):
    try:
        response = requests.get(
            WEATHER_SERVICE.format(
                BASE_URL=BASE_URL, city_name=city_name, API_KEY=API_KEY
            )
        ).json()
    except requests.exceptions.ConnectTimeout:
        console.print("[bold red]Unable to connect. Please try again later.[/]")
        return None

    if response["cod"] in ("400", "404"):
        if not compare:
            error_message = f"[bold red]{response['message'].capitalize()}[/]"
            console.print(error_message)
        return None
    return response


def get_wind_direction(angle: int) -> str:
    if angle in ORDINARY_WIND_ANGLES:
        for direction, value in ORDINARY_WIND_DIRECTIONS.items():
            if angle == value:
                return direction + f" ({angle}°)"
    else:
        for direction, (min, max) in SPECIFIC_WIND_DIRECTIONS.items():
            if min < angle < max:
                return direction + f" ({angle}°)"
    return "(Invalid wind direction)"


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
        f"{city_name.title().strip()} is {WEATHERS[weather_descriptions['weather_status']]} today. ({weather_descriptions['weather_description']})"
    )
    if unit_preference in ("2", "f"):
        temperature_fahrenheit = from_celsius_convert_to_fahrenheit(
            float(weather_descriptions["temperature_celsius"])
        )

        console.print(f"Temperature: {temperature_fahrenheit:.2f}[bold cyan]°F[/]")
    else:
        console.print(
            f"Temperature: {weather_descriptions['temperature_celsius']:.2f}[bold cyan]°C[/]"
        )
    console.print(f"Humidity: {weather_descriptions['humidity']}[bold cyan]%[/]")
    console.print(
        f"Wind speed: [bold cyan]{weather_descriptions['wind_speed']}m/s[/] (Direction: [bold cyan]{get_wind_direction(weather_descriptions['wind_direction'])}[/])"
    )
    console.input("[blue]Press enter to continue.[/]")
    console.print()


@app.command()
def check_weather(
    city: str = typer.Argument(..., help="Name of city to be checked"),
    unit: UnitType = typer.Argument(
        UnitType.CELSIUS, help="Unit preference in degree Celsius/Fahrenheit"
    ),
) -> None:
    """Get weather, temperature, humdity, wind speed of the city"""
    response = call_api(city)
    if response is None:
        console.print(f"No response for city {city}.")
        raise typer.Abort()

    print_weather_descriptions(response, city, unit)
    console.rule()


def get_six_days_for_forecast():
    six_days_list = []
    for i in range(0, 6):
        six_days_list.append(str(CURRENT_DAY + timedelta(days=i))[:10])
    return six_days_list


def parse_forecast_response(forecast_response, six_days_list):
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
    return temperature_and_weather_forecast


@app.command()
def check_forecast(
    city: str = typer.Argument(..., help="Name of the city to be forecasted"),
    unit: UnitType = typer.Argument(
        UnitType.CELSIUS, help="Unit preference in degree Celsius/Fahrenheit"
    ),
):
    """Get a 6 day temperature and weather forecast of the city"""
    response = call_api(city)
    if response is None:
        console.print(f"No response for city {city}.")
        raise typer.Abort()

    forecast_response = requests.get(
        FORECAST_SERVICE.format(
            BASE_URL=BASE_URL,
            lat=response["coord"]["lat"],
            lon=response["coord"]["lon"],
            API_KEY=API_KEY,
        )
    ).json()

    six_days_list = get_six_days_for_forecast()
    temperature_and_weather_forecast = parse_forecast_response(
        forecast_response, six_days_list
    )
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
        if unit == UnitType.FAHRENHEIT:
            unit_symbol = "°F"
            average_temperature = from_celsius_convert_to_fahrenheit(
                average_temperature
            )
        else:
            unit_symbol = "°C"
        console.print(
            f"The average temperature will be {average_temperature:.2f}{unit_symbol}."
        )
        console.print()
    six_days_list.clear()
    temperature_and_weather_forecast.clear()
    console.input("[blue]Press enter to continue.[/]")
    console.print()
    console.rule()


def print_compared_weather(
    first_city_name, first_city_info, second_city_name, second_city_info
):
    if (
        WEATHERS[first_city_info["weather_status"]]
        == WEATHERS[second_city_info["weather_status"]]
    ):
        console.print(
            f"Both {first_city_name} and {second_city_name} is {WEATHERS[first_city_info['weather_status']]}"
        )
    else:
        console.print(
            f"{first_city_name} is {WEATHERS[first_city_info['weather_status']]}, while {second_city_name} is {WEATHERS[second_city_info['weather_status']]}."
        )


def print_compared_temperature(
    first_city_name, first_city_info, second_city_name, second_city_info, unit
):
    first_city_temp = first_city_info["temperature_celsius"]
    second_city_temp = second_city_info["temperature_celsius"]
    difference = first_city_temp - second_city_temp
    if unit == UnitType.FAHRENHEIT:
        difference *= 9 / 5
        unit_symbol = "°F"
        first_city_temp = from_celsius_convert_to_fahrenheit(first_city_temp)
        second_city_temp = from_celsius_convert_to_fahrenheit(second_city_temp)
    else:
        unit_symbol = "°C"
    if difference < 0:
        console.print(
            f"{first_city_name}({first_city_temp:.2f}{unit_symbol}) is {abs(difference):.2f} {unit_symbol} colder than {second_city_name}({second_city_temp:.2f}{unit_symbol})."
        )
    elif difference > 0:
        console.print(
            f"{first_city_name}({first_city_temp:.2f}{unit_symbol}) is {difference:.2f} {unit_symbol} colder than {second_city_name}({second_city_temp:.2f}{unit_symbol})."
        )
    else:
        console.print(
            f"{first_city_name} has the same temperaure as {second_city_name} ({second_city_temp:.2f}{unit_symbol})."
        )


@app.command()
def compare_weather(
    first_city: str = typer.Argument(..., help="First city to compare with"),
    second_city: str = typer.Argument(..., help="Second city to compare with"),
    unit: UnitType = typer.Argument(
        UnitType.CELSIUS, help="Unit preference in degree Celsius/Fahrenheit"
    ),
    feature: Comparison_Features = typer.Argument(
        Comparison_Features.ALL, help="Temperature or Weather of the cities"
    ),
):
    """Compare city's temperature and weather forecast against another city"""
    console.print()
    response = call_api(first_city, compare=True)
    if response is None:
        console.print("[bold red]The first city name is invalid.[/]")
        raise typer.Abort()
    first_city_name = first_city.title().strip()
    first_city_info = get_weather_descriptions(response)

    second_response = call_api(second_city, compare=True)
    if second_response is None:
        console.print("[bold red]The second city name is invalid.[/]")
        raise typer.Abort()
    second_city_name = second_city.title().strip()
    second_city_info = get_weather_descriptions(second_response)

    if feature == Comparison_Features.WEATHER:
        print_compared_weather(
            first_city_name, first_city_info, second_city_name, second_city_info
        )
    elif feature == Comparison_Features.TEMPERATURE:
        print_compared_temperature(
            first_city_name, first_city_info, second_city_name, second_city_info, unit
        )
    elif feature == Comparison_Features.ALL:
        print_compared_weather(
            first_city_name, first_city_info, second_city_name, second_city_info
        )
        print_compared_temperature(
            first_city_name, first_city_info, second_city_name, second_city_info, unit
        )
    else:
        console.print("[bold red]Invalid input.[/]")
    console.print()
    console.rule()


def get_all_cities() -> None:
    """store all city name into a list"""
    with open("cities2.txt", "r", encoding="utf-8") as file:
        for city_name in file:
            city_list.append(city_name.rstrip())


if __name__ == "__main__":
    app()
