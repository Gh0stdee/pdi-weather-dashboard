import requests
import typer

from .mappings import (
    WEATHERS,
    Comparison_Feature,
    UnitType,
    from_celsius_convert_to_fahrenheit,
    from_kelvin_convert_to_celsius,
    get_five_days_for_forecast,
    get_weather_descriptions,
    parse_forecast_response,
)
from .output import (
    console,
    print_compared_temperature,
    print_compared_weather,
    print_weather_descriptions,
)
from .weather_api import API_KEY, BASE_URL, FORECAST_SERVICE, API_Response, call_api

app = typer.Typer()


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

    forecast_response = requests.get(
        FORECAST_SERVICE.format(
            BASE_URL=BASE_URL,
            lat=response[API_Response.JSON]["coord"]["lat"],
            lon=response[API_Response.JSON]["coord"]["lon"],
            API_KEY=API_KEY,
        )
    ).json()

    five_days_list = get_five_days_for_forecast()
    temperature_and_weather_forecast = parse_forecast_response(
        forecast_response, five_days_list
    )
    console.print()
    for day_index, (temperatures_of_the_day, weather_counts_of_the_day) in enumerate(
        temperature_and_weather_forecast
    ):
        console.print(f"[{five_days_list[day_index]}]")
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
    console.rule()
