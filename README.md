
# pdi-weather-dashboard

The weather dashboard uses weather API from [OpenWeather](https://openweathermap.org/)

Functionalities can be called with command line interface (enabled using [Typer](https://typer.tiangolo.com/))

Fuzzy search is supported for misspelled city name

## Setup

```
$ git clone git@github.com:Gh0stdee/pdi-weather-dashboard.git
$ cd pdi-weather-dashboard
$ uv sync --all-extras
# set api key
$ cp .env-template .env
# run the app
$ uv run main.py --help
# run the tests
$ uv run pytest
# check type hints
$ uv run ty check .
$ uv run mypy .
```

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
