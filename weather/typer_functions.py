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
from .weather_api import NONE_OPTION, call_api, call_forecast_api, parse_api_response

app = typer.Typer()


@app.command()
def check_weather(
    city: str = typer.Argument(..., help="Name of city to be checked"),
    unit: UnitType = typer.Option(
        UnitType.CELSIUS, help="Unit preference in degree Celsius/Fahrenheit"
    ),
) -> None:
    """Get weather, temperature, humdity, wind speed of the city"""
    response = parse_api_response(
        first_response_json=call_api(city), compare=False, city=city
    )
    if response.json is None or response.city == NONE_OPTION:
        raise typer.Abort()
    print_weather_descriptions(response.json, response.city, unit)
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
    response = parse_api_response(
        first_response_json=call_api(first_city), compare=True, city=first_city
    )
    if response.city == NONE_OPTION:
        raise typer.Abort()
    if response.json is None:
        console.print("[bold red]The first city name is invalid.[/]")
        raise typer.Abort()
    first_city_name = response.city.title().strip()
    first_city_info = get_weather_descriptions(response.json)

    second_response = parse_api_response(
        first_response_json=call_api(second_city), compare=True, city=second_city
    )
    if second_response.city == NONE_OPTION:
        raise typer.Abort()
    if second_response.json is None:
        console.print("[bold red]The second city name is invalid.[/]")
        raise typer.Abort()
    second_city_name = second_response.city.title().strip()
    second_city_info = get_weather_descriptions(second_response.json)

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
    forecast_response = call_forecast_api(city)
    five_days_list = get_five_days_for_forecast()
    forecast_days = parse_forecast_response(forecast_response.json, five_days_list)
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
