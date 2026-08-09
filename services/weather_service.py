import requests


class WeatherService:

    def get_weather(self, latitude: float, longitude: float):

        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code,wind_speed_10m",
            "timezone": "auto"
        }

        response = requests.get(url, params=params)

        response.raise_for_status()

        data = response.json()

        current = data["current"]

        return {
            "temperature": current["temperature_2m"],
            "wind_speed": current["wind_speed_10m"],
            "weather_code": current["weather_code"],
            "description": self.get_weather_description(
                current["weather_code"]
            )
        }

    def get_weather_description(self, code: int) -> str:

        weather_codes = {
            0: "Cielo despejado",
            1: "Principalmente despejado",
            2: "Parcialmente nublado",
            3: "Nublado",
            45: "Niebla",
            48: "Niebla con escarcha",
            51: "Llovizna ligera",
            53: "Llovizna moderada",
            55: "Llovizna intensa",
            56: "Llovizna helada ligera",
            57: "Llovizna helada intensa",
            61: "Lluvia ligera",
            63: "Lluvia moderada",
            65: "Lluvia intensa",
            66: "Lluvia helada ligera",
            67: "Lluvia helada intensa",
            71: "Nevada ligera",
            73: "Nevada moderada",
            75: "Nevada intensa",
            77: "Granizo de nieve",
            80: "Chubascos ligeros",
            81: "Chubascos moderados",
            82: "Chubascos intensos",
            85: "Chubascos de nieve ligeros",
            86: "Chubascos de nieve intensos",
            95: "Tormenta",
            96: "Tormenta con granizo ligero",
            99: "Tormenta con granizo intenso"
        }

        return weather_codes.get(
            code,
            "Condiciones meteorológicas desconocidas"
        )