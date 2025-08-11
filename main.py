import requests
from decouple import config
from rich import print
from rich.console import Console

WEATHER_SERVICE = (
    "https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}"
)
FORECAST_SERVICE = "https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}"
API_KEY = config("API_KEY")

console = Console()

functions = [
    "Weather Description [bold blue](w)[/]",
    "Weather Forecast [bold blue](f)[/]",
    "Weather Comparison [bold blue](c)[/]",
    "Check Another City [bold red](q)[/]",
]
units = ["Degree Celcius °C [bold blue](default)[/]", "Fahrenheit °F [bold blue](f)[/]"]
weathers = {
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

checked_cities = []


def get_wind_direction(angle: int) -> str:
    if angle == 0:
        return f"N ({angle}°)"
    elif angle < 45:
        return f"NNE ({angle}°)"
    elif angle == 45:
        return f"NE ({angle}°)"
    elif angle < 90:
        return f"ENE({angle}°)"
    elif angle == 90:
        return f"E ({angle}°)"
    elif angle < 135:
        return f"ESE ({angle}°)"
    elif angle == 135:
        return f"SE ({angle}°)"
    elif angle < 180:
        return f"SSE ({angle}°)"
    elif angle == 180:
        return f"S ({angle}°)"
    elif angle < 225:
        return f"SSW ({angle}°)"
    elif angle == 225:
        return f"SW ({angle}°)"
    elif angle < 270:
        return f"WSW ({angle}°)"
    elif angle == 270:
        return f"W ({angle}°)"
    elif angle < 315:
        return f"WNW ({angle}°)"
    elif angle == 315:
        return f"NW ({angle}°)"
    else:
        return f"NNW ({angle}°)"


def print_weather_descriptions(
    response: list, city_name: str, unit_preference: str
) -> None:
    """Printing weather descriptions(weather, temperature and humidity)"""
    weather_status = response["weather"][0]["main"]
    weather_description = response["weather"][0]["description"].capitalize()
    temperature_celsius = response["main"]["temp"] - 273.15
    humidity = response["main"]["humidity"]
    wind_speed = response["wind"]["speed"]
    wind_direction = response["wind"]["deg"]
    print()
    print(
        f"{city_name.title()} is {weathers[weather_status]} today. ({weather_description})"
    )
    if unit_preference == "f" or unit_preference == "2":
        temperature_fahrenheit = "{:.2f}".format(
            9 / 5 * float(temperature_celsius) + 32
        )
        console.print(f"Temperature: {temperature_fahrenheit}[bold cyan]°F[/]")
    else:
        temperature_celsius = "{:.2f}".format(temperature_celsius)
        print(f"Temperature: {temperature_celsius}[bold cyan]°C[/]")
    print(f"Humidity: {humidity}[bold cyan]%[/]")
    print(
        f"Wind speed: [bold cyan]{wind_speed}m/s[/] (Direction: [bold cyan]{get_wind_direction(wind_direction)}[/])"
    )
    input("Press enter to continue.")
    print()


def get_unit_preference():
    print("Which unit system do you prefer")
    for index, unit in list(enumerate(units, start=1)):
        console.print(f"{index}. {unit}")
    return input().strip().lower()


def check_city_weather(city_name, response) -> None:
    unit_preference = get_unit_preference()
    print_weather_descriptions(response, city_name, unit_preference)
    console.rule()


def check_weather_forecast(response):
    forecast_response = requests.get(
        FORECAST_SERVICE.format(
            lat=response["coord"]["lon"], lon=response["coord"]["lat"], API_KEY=API_KEY
        )
    ).json()
    print(forecast_response)


def function_select(city_name: str, response) -> None:
    """Select from functions"""
    function_choice = None
    while function_choice != "q":
        print("Select a function:")
        for number, function in list(enumerate(functions, start=1)):
            console.print(f"{number}. {function}")
            print()
        function_choice = input().strip().lower()[:1]
        print()
        if function_choice == "w" or function_choice == "1":
            console.rule()
            check_city_weather(city_name, response)
        elif function_choice == "f" or function_choice == "2":
            console.rule()
            check_weather_forecast(response)
        elif function_choice == "c" or function_choice == "3":
            pass


def main():
    print("Welcome to your weather dashboard.")
    print()
    while True:
        city_name = (
            console.input("Input a city name: [bold red](q to quit)[/] ")
            .strip()
            .lower()
        )
        if city_name == "q":
            break
        else:
            try:
                response = requests.get(
                    WEATHER_SERVICE.format(city_name=city_name, API_KEY=API_KEY)
                ).json()
            except requests.ConnectTimeoutError:
                console.print("[bold red]Unable to connect. Please try again later.[/]")
            if response["cod"] == "404":
                error_message = f"[bold red]{response['message'].capitalize()}[/]"
                console.print(error_message)
            elif response["cod"] == 200:
                print()
                function_select(city_name, response)


if __name__ == "__main__":
    main()
