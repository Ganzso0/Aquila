from agents.base_agent import BaseAgent
from core.result import AgentResult
from services.weather_service import WeatherService
from services.location_service import LocationService


class Poseidon(BaseAgent):
    """
    Agente encargado de proporcionar información meteorológica.
    """

    def __init__(self):

        super().__init__(
            name="Poseidon",
            description="Agente encargado de clima.",
            capabilities=[
                "weather"
            ],
            priority=1
        )

        self.weather = WeatherService()
        self.location = LocationService()

    def can_handle(self, request: str) -> bool:
        """
        Determina si Poseidon puede responder a la petición.
        """

        keywords = [
            "tiempo",
            "clima",
            "temperatura"
        ]

        request = request.lower()

        return any(
            keyword in request
            for keyword in keywords
        )

    def extract_location(self, request: str) -> str | None:

        request = request.lower()

        phrases = [
        "tiempo en ",
        "tiempo hace en ",
        "clima en ",
        "clima hace en ",
        "temperatura en ",
        "temperatura hace en "
        ]

        for phrase in phrases:

            if phrase in request:

                place = request.split(phrase, 1)[1]

                return place.strip(" ?¿!.,").title()

        return None

    def execute(self, request: str) -> AgentResult:

        place = self.extract_location(request)

        print("Lugar extraído:", repr(place))

    # =====================================
    # Obtener ubicación
    # =====================================

        if place is not None:

            print("Buscando ubicación:", place)

            location = self.location.get_location(place)

        else:

            print("No se indicó ubicación.")
            print("Obteniendo ubicación del dispositivo...")

        location = self.location.get_device_location()

        print("Resultado LocationService:", location)

    # =====================================
    # Comprobar ubicación
    # =====================================

        if location is None:

            print("ERROR: No se pudo obtener la ubicación.")

            return AgentResult(
            success=False,
            agent_name=self.name,
            type="information",
            message="No se pudo obtener la ubicación.",
            data={
                "response": (
                    "No he podido determinar tu ubicación."
                )
            }
        )

        print("Latitud:", location["latitude"])
        print("Longitud:", location["longitude"])

    # =====================================
    # Obtener tiempo
    # =====================================

        print("Consultando WeatherService...")

        weather = self.weather.get_weather(
        location["latitude"],
        location["longitude"]
        )

        print("Resultado WeatherService:", weather)

        if weather is None:

            print("ERROR: WeatherService no devolvió datos.")

            return AgentResult(
            success=False,
            agent_name=self.name,
            type="information",
            message="No se pudo obtener el tiempo.",
            data={
                "response": (
                    "No he podido obtener la información meteorológica."
                )
            }
        )

    # =====================================
    # Preparar respuesta
    # =====================================

        temperature = weather["temperature"]
        wind = weather["wind_speed"]
        description = weather["description"]

        location_name = location["name"]

        if location_name is None:
            location_name = "tu ubicación"

        return AgentResult(
        success=True,
        agent_name=self.name,
        type="information",
        message="Información meteorológica obtenida.",
        data={
            "response": (
                f"En {location_name} hay "
                f"{temperature} °C, "
                f"{description.lower()}, "
                f"con viento de {wind} km/h."
            ),
            "weather": weather,
            "location": location
        }
    )