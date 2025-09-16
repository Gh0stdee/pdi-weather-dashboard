
# pdi-weather-dashboard

The weather dashboard uses weather API from [OpenWeather](https://openweathermap.org/)

Functionalities can be called with command line interface (enabled using [Typer](https://typer.tiangolo.com/))

Fuzzy search is supported for misspelled city name

## Setup
```
git clone https://github.com/Gh0stdee/pdi-weather-dashboard.git
cd ./pdi-weather-dashboard
echo . > .env
uv sync
```

### Get an API key

1. Sign up at [OpenWeather](https://openweathermap.org/)

2. Generate key at [OpenWeatherAPIkey](https://home.openweathermap.org/api_keys)

<img width="560" height="720" alt="image" src="https://github.com/user-attachments/assets/dd303801-0b9c-491a-bb81-640c475fb571" />


### Add API key inside .env 

```API_KEY = "012345..."```

### Select UTF-8 if other encoding is chosen

<img width="560" height="720" alt="image" src="https://github.com/user-attachments/assets/e06ebaac-6738-4785-b84a-b6eb91e98ede" />

## Usage

### Interactive Mode Example:

```uv run main.py```

#### Select function from function Menu

<img width="280" height="= 180" alt="image" src="https://github.com/user-attachments/assets/81ea168e-14ab-4de9-a8eb-fd1136391f4a" />

#### Weather Details Function
<img width="280" height="180" alt="image" src="https://github.com/user-attachments/assets/1860960e-f05b-4f33-8f4a-b3e19ebc3886" />

#### Weather Forecast Function
<img width="280" height="360" alt="image" src="https://github.com/user-attachments/assets/d810d81c-3890-4049-8938-8d27e4765c3d" />

#### Weather Comparison Function
<img width="280" height="180" alt="image" src="https://github.com/user-attachments/assets/ac650ac7-8d79-45de-85f9-02ba12e581fe" />




### CLI

#### Current Weather

##### Prints the weather information of a city

```uv run ty-main.py check-weather "city_name" --unit=c/f```

> (Options: `c`->Celsius[Default], `f`->Fahrenheit)

---

#### Five Day Weather Forecast

##### Prints a five day weather forecast report of a city

```uv run ty-main.py check-forecast "city_name" --unit=c/f```

> (Options: `c`->Celsius[Default], `f`->Fahrenheit)

---

#### Compare Different Cities' Weathers

##### Print the difference in weather between two cities

```uv run ty-main.py check-comparison "first_city_name" "second_city_name"--unit=c/f --feature=a/w/t```

> (Options: `c`->Celsius[Default], `f`->Fahrenheit; `a`->all[default], `w`->weather, `t`->temperature)
