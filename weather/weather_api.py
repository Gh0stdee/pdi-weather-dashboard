from enum import StrEnum
from typing import NamedTuple

import requests
import requests_cache
from decouple import config
from typer import Abort

from .mappings import fuzzy_search
from .output import console

BASE_URL = "https://api.openweathermap.org/data/2.5/"
WEATHER_SERVICE = "{BASE_URL}weather?q={city_name}&appid={API_KEY}"
FORECAST_SERVICE = "{BASE_URL}forecast?lat={lat}&lon={lon}&appid={API_KEY}"
API_KEY = config("API_KEY")
# TODO: see if we can break out rich which is related to formattting, not data
# processing
NONE_OPTION = "[red]None of the above[/]"

ONE_DAY = 86400
requests_cache.install_cache("cache.db", backend="sqlite", expire_after=ONE_DAY)


class Connection_Error(StrEnum):
    BAD_REQUEST = "400"
    PAGE_NOT_FOUND = "404"


class ApiResponse(NamedTuple):
    json: dict | None
    city: str


def call_api(city: str, compare: bool = False) -> ApiResponse:
    """Tries to call the API and return the parsed response"""
    try:
        first_response_json = requests.get(
            WEATHER_SERVICE.format(BASE_URL=BASE_URL, city_name=city, API_KEY=API_KEY)
        ).json()
    except requests.exceptions.ConnectTimeout:
        console.print("[bold red]Unable to connect. Please try again later.[/]")
        raise Abort()
    return parse_api_response(first_response_json, compare, city)


def call_forecast_api(city: str) -> ApiResponse:
    """Tries to call the Forecast API and return the received response"""
    response = call_api(city)
    if response.json is None or response.city == NONE_OPTION:
        raise Abort()

    forecast_response = requests.get(
        FORECAST_SERVICE.format(
            BASE_URL=BASE_URL,
            lat=response.json["coord"]["lat"],
            lon=response.json["coord"]["lon"],
            API_KEY=API_KEY,
        )
    )
    return ApiResponse(json=forecast_response.json(), city=response.city)


def handling_api_error_response(first_response_json, compare) -> None:
    """Print out error message from response json file"""
    if not compare:
        error_message = f"[bold red]{first_response_json['message'].capitalize()}[/]"
        console.print(error_message)
    return None


def parse_api_response(first_response_json, compare, city) -> ApiResponse:
    """Check if the api response and city name is valid"""
    if first_response_json["cod"] == Connection_Error.BAD_REQUEST:
        return_response_json = handling_api_error_response(first_response_json, compare)
    elif first_response_json["cod"] == Connection_Error.PAGE_NOT_FOUND:
        new_city_list = fuzzy_search(city.title().strip())
        if not new_city_list:  # [] is falsy
            return_response_json = handling_api_error_response(
                first_response_json, compare
            )
        else:
            if len(new_city_list) != 1:
                new_city = handling_multi_fuzzy_search_result(new_city_list, False)
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
    return ApiResponse(json=return_response_json, city=city)


def handling_multi_fuzzy_search_result(new_city_list: list[str], test: bool) -> str:
    """Ask user to choose which city they meant from the fuzzy search"""
    new_city_list.append(NONE_OPTION)
    for index, city in enumerate(new_city_list, start=1):
        console.print(f"{index}. {city}")
    while True:
        try:
            positive_numbered_index = int(console.input("Which city do you mean? ")) - 1
            if positive_numbered_index < 0:
                console.print(
                    ("[bold red]Please select from the given numbers only.[/]")
                )
                console.print()
                continue
            else:
                new_city = new_city_list[positive_numbered_index]
        except ValueError:
            console.print("[bold red]Please input numbers only.[/]")
            console.print()
            if test:
                raise
            else:
                continue
        except IndexError:
            console.print(("[bold red]Please select from the given numbers only.[/]"))
            console.print()
            if test:
                raise
            else:
                continue
        break
    return new_city
