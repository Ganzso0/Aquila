from skyfield.api import load, wgs84
from datetime import datetime
from zoneinfo import ZoneInfo


class AstronomyService:

    def __init__(self):

        self.ts = load.timescale()
        self.eph = load("de421.bsp")

        self.earth = self.eph["earth"]

        self.objects = {
            "sun": self.eph["sun"],
            "moon": self.eph["moon"],
            "mercury": self.eph["mercury"],
            "venus": self.eph["venus"],
            "mars": self.eph["mars"],
            "jupiter": self.eph["jupiter barycenter"],
            "saturn": self.eph["saturn barycenter"],
            "uranus": self.eph["uranus barycenter"],
            "neptune": self.eph["neptune barycenter"],
        }

    def get_object(
        self,
        object_name: str,
        latitude: float,
        longitude: float,
        date: str,
        time: str
    ):

        object_name = object_name.lower()

        if object_name not in self.objects:
            return None

        local_time = datetime.fromisoformat(
            f"{date}T{time}"
        ).replace(
            tzinfo=ZoneInfo("Europe/Madrid")
        )

        skyfield_time = self.ts.from_datetime(local_time)

        observer = self.earth + wgs84.latlon(
            latitude,
            longitude
        )

        astrometric = observer.at(skyfield_time).observe(
            self.objects[object_name]
        )

        apparent = astrometric.apparent()

        altitude, azimuth, distance = apparent.altaz()

        return {
            "object": object_name,
            "altitude": altitude.degrees,
            "azimuth": azimuth.degrees,
            "distance_au": distance.au
        }