from rich.console import Console

from .mappings import (
    WEATHERS,
    UnitType,
    from_celsius_convert_to_fahrenheit,
    get_weather_descriptions,
    get_wind_direction,
)

console = Console()


def print_weather_descriptions(
    response: dict, city_name: str, unit_preference: str
) -> None:
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


def print_compared_temperature(
    first_city_name: str,
    first_city_info: dict,
    second_city_name: str,
    second_city_info: dict,
    unit: UnitType,
):
    """Print out the two cities' temperatures"""
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
