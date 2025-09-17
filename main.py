from enum import StrEnum

import requests_cache

import weather.weather_api as api
from weather.mappings import (
    WEATHERS,
    UnitType,
    from_celsius_convert_to_fahrenheit,
    from_kelvin_convert_to_celsius,
    get_five_days_for_forecast,
    get_weather_descriptions,
    parse_forecast_response,
)
from weather.output import (
    console,
    print_compared_temperature,
    print_compared_weather,
    print_weather_descriptions,
)
from weather.weather_api import NONE_OPTION

ONE_DAY = 86400
requests_cache.install_cache("cache.db", backend="sqlite", expire_after=ONE_DAY)


class DashboardFunctionsStr(StrEnum):
    WEATHER_DETAILS = "d"
    WEATHER_FORECAST = "f"
    WEATHER_COMPARISON = "c"
    QUIT = "q"


class DashboardFunctionsInt(StrEnum):
    WEATHER_DETAILS = "1"
    WEATHER_FORECAST = "2"
    WEATHER_COMPARISON = "3"
    QUIT = "4"


FUNCTIONS = [
    "Weather Details [bold blue](d)[/]",
    "Weather Forecast [bold blue](f)[/]",
    "Weather Comparison [bold blue](c)[/]",
    "QUIT [bold red](q)[/]",
]

INVALID_INPUT = "[bold red]Invalid Input! Please insert again![/]"


def hold():
    console.input("Press enter to continue.")


UNITS: list[str] = [
    "Degree Celcius °C [bold blue](default)[/]",
    "Fahrenheit °F [bold blue](f)[/]",
]


def get_unit_preference() -> UnitType:
    for index, unit in enumerate(UNITS, start=1):
        console.print(f"{index}. {unit}")
    unit = console.input("\nPlease select a unit system: ")
    console.print()
    if unit in (UnitType.FAHRENHEIT_CHAR, UnitType.FAHRENHEIT_INDEX):
        return UnitType.FAHRENHEIT_CHAR
    return UnitType.CELSIUS


def print_forecast(forecast_days, five_days_list, unit):
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
        if unit == UnitType.FAHRENHEIT_CHAR:
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


def main():
    console.print("Welcome to your weather dashboard.\n")
    while True:
        for index, function in enumerate(FUNCTIONS, start=1):
            console.print(f"{index}. {function}")
        choice = console.input("\nPlease choose a function: ").lower().strip()
        if choice in (
            DashboardFunctionsInt.WEATHER_DETAILS,
            DashboardFunctionsStr.WEATHER_DETAILS,
        ):
            city = console.input("\nInput the city to be checked: ")
            response = api.parse_api_response(
                first_response_json=api.call_api(city, False), compare=False, city=city
            )
            if response.json is not None and response.city != NONE_OPTION:
                console.print()
                unit = get_unit_preference()
                print_weather_descriptions(response.json, response.city, unit)
                hold()
            console.rule()
            console.print()
        elif choice in (
            DashboardFunctionsInt.WEATHER_FORECAST,
            DashboardFunctionsStr.WEATHER_FORECAST,
        ):
            city = console.input("\nInput the city to be checked: ")
            forecast_response = api.call_forecast_api(city, False)
            if forecast_response is not None:
                five_days_list = get_five_days_for_forecast()
                forecast_days = parse_forecast_response(
                    forecast_response.json, five_days_list
                )
                unit = get_unit_preference()
                print_forecast(forecast_days, five_days_list, unit)
                hold()
            console.rule()
            console.print()
        elif choice in (
            DashboardFunctionsInt.WEATHER_COMPARISON,
            DashboardFunctionsStr.WEATHER_COMPARISON,
        ):
            first_city = console.input("\nInput the first city: ")
            while True:
                response = api.parse_api_response(
                    first_response_json=api.call_api(first_city, False),
                    compare=True,
                    city=first_city,
                )
                if response.city == NONE_OPTION:
                    first_city = console.input("\nPlease re-input the first city: ")
                    continue
                if response.json is None:
                    console.print("[bold red]The first city name is invalid.[/]")
                    first_city = console.input("\nPlease re-input the first city: ")
                    continue
                break
            first_city_name = response.city.title().strip()
            first_city_info = get_weather_descriptions(response.json)
            second_city = console.input("Input the second city: ")
            console.print()
            while True:
                second_response = api.parse_api_response(
                    first_response_json=api.call_api(second_city, False),
                    compare=True,
                    city=second_city,
                )
                if second_response.city == NONE_OPTION:
                    second_city = console.input("\nPlease re-input the second city: ")
                    continue
                if second_response.json is None:
                    console.print("[bold red]The second city name is invalid.[/]")
                    second_city = console.input("\nPlease re-input the second city: ")
                    continue
                break
            second_city_name = second_response.city.title().strip()
            second_city_info = get_weather_descriptions(second_response.json)
            unit = get_unit_preference()
            print_compared_weather(
                first_city_name, first_city_info, second_city_name, second_city_info
            )
            print_compared_temperature(
                first_city_name,
                first_city_info,
                second_city_name,
                second_city_info,
                unit,
            )
            console.print()
            hold()
            console.rule()
        elif choice in (DashboardFunctionsInt.QUIT, DashboardFunctionsStr.QUIT):
            console.rule()
            break
        else:
            console.print(INVALID_INPUT)
            console.rule()
            console.print()


if __name__ == "__main__":
    main()
