from services.weather_service import WeatherService


weather = WeatherService()

data = weather.get_weather("Madrid")

print(data)