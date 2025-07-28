import requests

API_KEY = "a2e1a6d91f113b9e8f9baca3ad3f2dfa"
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


def get_city_name() -> str:
    """Ask user for a city name"""
    return input("Input city name: ")


def get_weather(city_name: str) -> None:
    """Get the weather info for a city"""
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather?q="
        + city_name
        + "&appid="
        + API_KEY
    )
    try:
        weather_status = response.json()["weather"][0]["main"]
        print(f"{city_name.title()} is {weathers[weather_status]} today.")
    except KeyError:
        print("Invalid input.")


def check_another_city() -> bool:
    """Ask the user if they want to check another city's weather"""
    print()
    response = input("Would you want to check another city's weather? (y/n) ")
    if response.lower() == "n":
        print("Goodbye!")
        return False
    elif response.lower() == "y":
        return True
    else:
        print("Invalid input.")
        return check_another_city()


def main():
    print("Hello! Which city's weather do you want to check today?")
    check_weather = True
    while check_weather:
        get_weather(get_city_name())
        check_weather = check_another_city()
        print()


if __name__ == "__main__":
    main()
