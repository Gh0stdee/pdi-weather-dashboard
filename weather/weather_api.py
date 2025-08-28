from enum import IntEnum, StrEnum

import requests
from decouple import config
from rich.console import Console
from typer import Abort

from .mappings import fuzzy_search

BASE_URL = "https://api.openweathermap.org/data/2.5/"
WEATHER_SERVICE = "{BASE_URL}weather?q={city_name}&appid={API_KEY}"
FORECAST_SERVICE = "{BASE_URL}forecast?lat={lat}&lon={lon}&appid={API_KEY}"
API_KEY = config("API_KEY")
console = Console()


class Connection_Error(StrEnum):
    BAD_REQUEST = "400"
    PAGE_NOT_FOUND = "404"


class API_Response(IntEnum):
    JSON = 0
    CITY = 1


def call_api(city: str, compare: bool = False):
    try:
        first_response_json = requests.get(
            WEATHER_SERVICE.format(BASE_URL=BASE_URL, city_name=city, API_KEY=API_KEY)
        ).json()
    except requests.exceptions.ConnectTimeout:
        console.print("[bold red]Unable to connect. Please try again later.[/]")
        raise Abort()
    return parse_api_response(first_response_json, compare, city)


def handling_api_error_response(first_response_json, compare) -> None:
    if not compare:
        error_message = f"[bold red]{first_response_json['message'].capitalize()}[/]"
        console.print(error_message)
    return None


def parse_api_response(first_response_json, compare, city) -> list:
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
    else:
        return_response_json = first_response_json

    return [return_response_json, city]


def handling_multi_fuzzy_search_result(new_city_list: list[str]) -> str:
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
