# mappings.py
from collections import Counter
from datetime import datetime, timedelta

# mappings.py
from difflib import get_close_matches

# weather_api.py
from enum import IntEnum, StrEnum

# weather_api.py
import requests
import requests_cache

# weather_api.py
import typer

# weather_api.py
from decouple import config

# weather_api.py
from rich.console import Console

# typer_functions.py
app = typer.Typer()

# weather_api.py
API_KEY = config("API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/"
WEATHER_SERVICE = (
    f"{BASE_URL}weather?appid={API_KEY}" + "&q={city_name}&appid={API_KEY}"
)
FORECAST_SERVICE = f"{BASE_URL}forecast?appid={API_KEY}" + "&lat={lat}&lon={lon}"

# weather_api.py
ONE_DAY = 86400
requests_cache.install_cache("cache.db", backend="sqlite", expire_after=ONE_DAY)

# mappings.py
INVALID_WIND_DIRECTION = "(Invalid wind direction)"


# typer_functions.py
class UnitType(StrEnum):
    CELSIUS = "c"
    FAHRENHEIT = "f"


# typer_functions.py
class Comparison_Feature(StrEnum):
    ALL = "a"
    WEATHER = "w"
    TEMPERATURE = "t"


# weather_api.py
class API_Response(IntEnum):
    JSON = 0
    CITY = 1


# weather_api.py
class Connection_Error(StrEnum):
    BAD_REQUEST = "400"
    PAGE_NOT_FOUND = "404"


# output.py
console = Console()

# mappings.py
CURRENT_DAY = datetime.now()
FIVE_DAYS = 5
DATE_INDEX = 10

# mappings.py
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

# mappings.py
ORDINARY_WIND_ANGLES: list[int] = [0, 45, 90, 135, 180, 225, 270, 315]

# mappings.py
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

# mappings.py
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


# mappings.py
class forecast_day:
    def __init__(self):
        self.temperatures = []
        self.forecast_weather_counter = Counter()
        self.entry_numbers = 0

    def update_forecast_info(self, weather_count: list[str], temperature: float):
        self.temperatures.append(temperature)
        self.forecast_weather_counter.update(weather_count)
        self.entry_numbers += 1


# mappings.py
def from_kelvin_convert_to_celsius(temperature: float) -> float:
    return temperature - 273.15


# mappings.py
def from_celsius_convert_to_fahrenheit(temperature: float) -> float:
    return temperature * 9 / 5 + 32


# mappings.py
def fuzzy_search(city: str) -> list[str]:
    """Return a list of city names that is close to search input"""
    new_search = get_close_matches(city, get_all_cities())
    if len(new_search) < 1:
        return None
    else:
        return new_search


# weather_api.py
def call_api(city: str, compare: bool = False) -> list:
    """Tries to call the API and return the parsed response"""
    try:
        first_response_json = requests.get(
            WEATHER_SERVICE.format(BASE_URL=BASE_URL, city_name=city, API_KEY=API_KEY)
        ).json()
    except requests.exceptions.ConnectTimeout:
        console.print("[bold red]Unable to connect. Please try again later.[/]")
        raise typer.Abort()
    return parse_api_response(first_response_json, compare, city)


def call_forecast_api(city: str):
    """Tries to call the Forecast API and return the received response"""
    response = call_api(city)
    if response[API_Response.JSON] is None:
        raise typer.Abort()

    forecast_response = requests.get(
        FORECAST_SERVICE.format(
            BASE_URL=BASE_URL,
            lat=response[API_Response.JSON]["coord"]["lat"],
            lon=response[API_Response.JSON]["coord"]["lon"],
            API_KEY=API_KEY,
        )
    ).json()
    return forecast_response


# weather_api.py
def handling_api_error_response(first_response_json, compare) -> None:
    """Print out error message from response json file"""
    if not compare:
        error_message = f"[bold red]{first_response_json['message'].capitalize()}[/]"
        console.print(error_message)
    return None


# weather_api.py
def parse_api_response(first_response_json, compare, city) -> list:
    """Check if the api response and city name is valid"""
    if first_response_json["cod"] == Connection_Error.BAD_REQUEST:
        return_response_json = handling_api_error_response(first_response_json, compare)
    elif first_response_json["cod"] == Connection_Error.PAGE_NOT_FOUND:
        new_city_list = fuzzy_search(city.title().strip())
        if new_city_list is None:
            return_response_json = handling_api_error_response(
                first_response_json, compare
            )
        else:
            if len(new_city_list) != 1:
                new_city = handling_multi_fuzzy_search_result(new_city_list)
            else:
                new_city = new_city_list[0]

            return_response_json = requests.get(
                WEATHER_SERVICE.format(
                    BASE_URL=BASE_URL, city_name=new_city, API_KEY=API_KEY
                )
            ).json()
            city = new_city
    else:
        return_response_json = first_response_json

    return [return_response_json, city]


# weather_api.py
def handling_multi_fuzzy_search_result(new_city_list: list[str]) -> str:
    """Ask user to choose which city they meant from the fuzzy search"""
    for index, city in enumerate(new_city_list, start=1):
        console.print(f"{index}. {city}")
    while True:
        try:
            new_city = new_city_list[int(console.input("Which city do you mean? ")) - 1]
        except ValueError:
            console.print("[bold red]Please input numbers only.[/]")
            console.print()
            continue
        except IndexError:
            console.print(("[bold red]Please select from the given numbers only.[/]"))
            console.print()
            continue
        break
    return new_city


# mappings.py
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


# weather_api.py
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


# output.py
def print_weather_descriptions(response, city_name: str, unit_preference: str) -> None:
    """Printing weather descriptions(weather, temperature and humidity)"""
    weather_descriptions = get_weather_descriptions(response)
    console.print()
    console.print(
        f"{city_name.title().strip()} is {WEATHERS[weather_descriptions['weather_status']]} today. ({weather_descriptions['weather_description']})"
    )
    if unit_preference == "f":
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


# typer_functions.py
@app.command()
def check_weather(
    city: str = typer.Argument(..., help="Name of city to be checked"),
    unit: UnitType = typer.Option(
        UnitType.CELSIUS, help="Unit preference in degree Celsius/Fahrenheit"
    ),
) -> None:
    """Get weather, temperature, humdity, wind speed of the city"""
    response = call_api(city)
    if response[API_Response.JSON] is None:
        raise typer.Abort()

    print_weather_descriptions(
        response[API_Response.JSON], response[API_Response.CITY], unit
    )
    console.print()
    console.rule()


# mappings.py
def get_five_days_for_forecast():
    five_days_list = []
    for i in range(0, FIVE_DAYS):
        five_days_list.append(str(CURRENT_DAY + timedelta(days=i))[:DATE_INDEX])
    return five_days_list


# mappings.py
def parse_forecast_response(forecast_response, five_days_list) -> list[forecast_day]:
    """Separate the response into five days"""
    first_day = forecast_day()
    second_day = forecast_day()
    third_day = forecast_day()
    fourth_day = forecast_day()
    fifth_day = forecast_day()
    for forecast_info in forecast_response["list"]:
        if forecast_info["dt_txt"][:DATE_INDEX] == five_days_list[0]:
            first_day.update_forecast_info(
                [forecast_info["weather"][0]["main"]], forecast_info["main"]["temp"]
            )
        elif forecast_info["dt_txt"][:DATE_INDEX] == five_days_list[1]:
            second_day.update_forecast_info(
                [forecast_info["weather"][0]["main"]], forecast_info["main"]["temp"]
            )
        elif forecast_info["dt_txt"][:DATE_INDEX] == five_days_list[2]:
            third_day.update_forecast_info(
                [forecast_info["weather"][0]["main"]], forecast_info["main"]["temp"]
            )
        elif forecast_info["dt_txt"][:DATE_INDEX] == five_days_list[3]:
            fourth_day.update_forecast_info(
                [forecast_info["weather"][0]["main"]], forecast_info["main"]["temp"]
            )
        elif forecast_info["dt_txt"][:DATE_INDEX] == five_days_list[4]:
            fifth_day.update_forecast_info(
                [forecast_info["weather"][0]["main"]], forecast_info["main"]["temp"]
            )
    return [first_day, second_day, third_day, fourth_day, fifth_day]


# typer_functions.py
@app.command()
def check_forecast(
    city: str = typer.Argument(..., help="Name of the city to be forecasted"),
    unit: UnitType = typer.Option(
        UnitType.CELSIUS, help="Unit preference in degree Celsius/Fahrenheit"
    ),
):
    """Get a 5 day temperature and weather forecast of the city"""
    response = call_api(city)
    if response[API_Response.JSON] is None:
        raise typer.Abort()

    forecast_response = call_forecast_api(city)
    five_days_list = get_five_days_for_forecast()
    forecast_days = parse_forecast_response(forecast_response, five_days_list)
    console.print()
    for day_index, forecast_day in enumerate(forecast_days):
        console.print(f"[{five_days_list[day_index]}]")
        if forecast_day.forecast_weather_counter.most_common(1)[0] == "Tornado":
            console.print(
                "[bold red]The city is likely to be hit by a tornado! Please stay safe![/]"
            )
        else:
            console.print(
                f"The weather on this day is mostly {WEATHERS[forecast_day.forecast_weather_counter.most_common(1)[0][0]]}."
            )
        average_temperature = from_kelvin_convert_to_celsius(
            sum(forecast_day.temperatures) / forecast_day.entry_numbers
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
    console.rule()


# output.py
def print_compared_weather(
    first_city_name: str,
    first_city_info: dict,
    second_city_name: str,
    second_city_info: dict,
):
    """Print out the two cities' weathers"""
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


# output.py
def print_compared_temperature(
    first_city_name: str,
    first_city_info: dict,
    second_city_name: str,
    second_city_info: dict,
    unit: UnitType,
):
    """Print out the tow cities' temperatures"""
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


# typer_functions.py
@app.command()
def check_comparison(
    first_city: str = typer.Argument(..., help="First city to compare with"),
    second_city: str = typer.Argument(..., help="Second city to compare with"),
    unit: UnitType = typer.Option(
        UnitType.CELSIUS, help="Unit preference in degree Celsius/Fahrenheit"
    ),
    feature: Comparison_Feature = typer.Option(
        Comparison_Feature.ALL, help="Temperature or Weather of the cities"
    ),
):
    """Compare city's temperature and weather forecast against another city"""
    console.print()
    response = call_api(first_city, compare=True)
    if response[API_Response.JSON] is None:
        console.print("[bold red]The first city name is invalid.[/]")
        raise typer.Abort()
    first_city_name = response[API_Response.CITY].title().strip()
    first_city_info = get_weather_descriptions(response[API_Response.JSON])

    second_response = call_api(second_city, compare=True)
    if second_response[API_Response.JSON] is None:
        console.print("[bold red]The second city name is invalid.[/]")
        raise typer.Abort()
    second_city_name = second_response[API_Response.CITY].title().strip()
    second_city_info = get_weather_descriptions(second_response[API_Response.JSON])

    if feature == Comparison_Feature.WEATHER:
        print_compared_weather(
            first_city_name, first_city_info, second_city_name, second_city_info
        )
    elif feature == Comparison_Feature.TEMPERATURE:
        print_compared_temperature(
            first_city_name, first_city_info, second_city_name, second_city_info, unit
        )
    elif feature == Comparison_Feature.ALL:
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


# mappings.py
def get_all_cities() -> list[str]:
    """store all city name into a list"""
    city_list = []
    with open("cities2.txt", "r", encoding="utf-8") as file:
        for city_name in file:
            city_list.append(city_name.rstrip())
    return city_list


if __name__ == "__main__":
    app()
