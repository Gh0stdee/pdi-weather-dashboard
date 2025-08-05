# from decouple import config

BASE_URL = "https://api.openweathermap.org/data/2.5/"
WEATHER_SERVICE = "{BASE_URL}weather?q={city_name}&appid={API_KEY}"
FORECAST_SERVICE = "{BASE_URL}forecast?lat={lat}&lon={lon}&appid={API_KEY}"
# API_KEY = config("API_KEY")
