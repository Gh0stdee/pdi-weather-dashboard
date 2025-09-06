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

ONE_DAY = 86400
requests_cache.install_cache("cache.db", backend="sqlite", expire_after=ONE_DAY)


class Connection_Error(StrEnum):
    BAD_REQUEST = "400"
    PAGE_NOT_FOUND = "404"


class api_response(NamedTuple):
    json: dict
    city: str


def call_api(city: str) -> dict:
    """Tries to call the API and return response in json format"""
    try:
        first_response_json = requests.get(
            WEATHER_SERVICE.format(BASE_URL=BASE_URL, city_name=city, API_KEY=API_KEY)
        ).json()
    except requests.exceptions.ConnectTimeout:
        console.print("[bold red]Unable to connect. Please try again later.[/]")
        raise Abort()
    return first_response_json


def call_forecast_api(city: str) -> api_response:
    """Tries to call the Forecast API and return the received response"""
    response = parse_api_response(
        first_response_json=call_api(city), compare=False, city=city
    )  # Call normal API to get latitude and longitude
    if response.json is None or response.city == "[red]None of the above[/]":
        raise Abort()

    """
    Response's info have been verified above, no need to parse again
    Return the api_response directly after calling forecast API
    """
    forecast_response = requests.get(
        FORECAST_SERVICE.format(
            BASE_URL=BASE_URL,
            lat=response.json["coord"]["lat"],
            lon=response.json["coord"]["lon"],
            API_KEY=API_KEY,
        )
    )
    return api_response(json=forecast_response.json(), city=response.city)


def handling_api_error_response(first_response_json: dict, compare: bool):
    """Print out error message from response json file"""
    if not compare:
        error_message = f"[bold red]{first_response_json['message'].capitalize()}[/]"
        console.print(error_message)
    return None


def parse_api_response(
    first_response_json: dict, compare: bool, city: str
) -> api_response:
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
    return api_response(json=return_response_json, city=city)


def handling_multi_fuzzy_search_result(new_city_list: list[str], test: bool) -> str:
    """Ask user to choose which city they meant from the fuzzy search"""
    new_city_list.append("[red]None of the above[/]")
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
