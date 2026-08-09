import requests 
from winrt.windows.devices.geolocation import (
    Geolocator,
    GeolocationAccessStatus
)
import asyncio


class LocationService:

    def get_location(self, place: str):

        url = "https://geocoding-api.open-meteo.com/v1/search"

        params = {
            "name": place,
            "count": 1,
            "language": "es",
            "format": "json"
        }

        response = requests.get(url, params=params)

        response.raise_for_status()

        data = response.json()

        if "results" not in data:
            return None

        result = data["results"][0]

        return {
            "name": result["name"],
            "country": result.get("country"),
            "latitude": result["latitude"],
            "longitude": result["longitude"]
        }

    def get_device_location(self):

        async def get_location():

            access_status = await Geolocator.request_access_async()

            if access_status != GeolocationAccessStatus.ALLOWED:
                return None

            locator = Geolocator()

            position = await locator.get_geoposition_async()

            coordinate = position.coordinate.point.position

            return {
            "latitude": coordinate.latitude,
            "longitude": coordinate.longitude
            }

        location = asyncio.run(get_location())

        if location is None:
            return None

        url = "https://nominatim.openstreetmap.org/reverse"

        params = {
        "lat": location["latitude"],
        "lon": location["longitude"],
        "format": "jsonv2",
        "accept-language": "es"
        }

        headers = {
        "User-Agent": "Lacerta/1.0"
        }

        response = requests.get(
        url,
        params=params,
        headers=headers
        )

        response.raise_for_status()

        data = response.json()

        address = data.get("address", {})

        return {
        "name": (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or address.get("county")
        ),
        "country": address.get("country"),
        "latitude": location["latitude"],
        "longitude": location["longitude"]
        }