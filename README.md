
# pdi-weather-dashboard

The weather dashboard uses weather API from [OpenWeather](https://openweathermap.org/)

Functionalities can be called with command line interface (enabled using [Typer](https://typer.tiangolo.com/))

Fuzzy search is supported for misspelled city name

## Setup

## Usage

### Current Weather

#### Prints the weather information of a city

```uv run main.py check-weather "city_name" --unit=c/f```

> (Options: `c`->Celsius[Default], `f`->Fahrenheit)

---

### Five Day Weather Forecast

#### Prints a five day weather forecast report of a city

```uv run main.py check-forecast "city_name" --unit=c/f```

> (Options: `c`->Celsius[Default], `f`->Fahrenheit)

---

### Compare Different Cities' Weathers

#### Print the difference in weather between two cities

```uv run main.py check-comparison "first_city_name" "second_city_name"--unit=c/f --feature=a/w/t```

> (Options: `c`->Celsius[Default], `f`->Fahrenheit; `a`->all[default], `w`->weather, `t`->temperature)
