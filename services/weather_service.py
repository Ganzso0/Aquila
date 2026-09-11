import requests
from datetime import datetime


class WeatherService:

    def get_weather(
        self,
        latitude: float,
        longitude: float,
        date: str
    ):

        today = datetime.now().date()
        requested_date = datetime.strptime(
            date,
            "%Y-%m-%d"
        ).date()

        # =====================================
        # Fecha pasada → API histórica
        # =====================================

        if requested_date < today:

            url = "https://archive-api.open-meteo.com/v1/archive"

        # =====================================
        # Hoy / futuro → API de previsión
        # =====================================

        else:

            url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "weather_code"
            ),
            "timezone": "auto",
            "start_date": date,
            "end_date": date
        }

        response = requests.get(
            url,
            params=params
        )

        response.raise_for_status()

        data = response.json()

        daily = data["daily"]

        weather_code = daily["weather_code"][0]

        return {
            "temperature_max": daily["temperature_2m_max"][0],
            "temperature_min": daily["temperature_2m_min"][0],
            "weather_code": weather_code,
            "description": self.get_weather_description(
                weather_code
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