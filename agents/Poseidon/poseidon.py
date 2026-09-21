from agents.base_agent import BaseAgent
from core.models.request import AgentRequest
from core.models.result import AgentResult
from services.external.weather_service import WeatherService
from services.external.location_service import LocationService


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

    def can_handle(self, request: AgentRequest) -> bool:
        """
        Determina si Poseidon puede responder a la petición.
        """

        return request.intent == "weather"

    def execute(self, request: AgentRequest) -> AgentResult:

        # raise Exception("Fallo de prueba de Aegis")

        # =====================================
        # Obtener ubicación solicitada
        # =====================================

        place = request.parameters.get("location")

        date = request.parameters.get("date")

        print("Ubicación recibida:", repr(place))
        print("Fecha recibida:", repr(date))

        

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

        if request.action == "current":

            weather = self.weather.get_current_weather(
                location["latitude"],
                location["longitude"]
            )

        elif request.action == "forecast":

            weather = self.weather.get_forecast(
                location["latitude"],
                location["longitude"],
                date
            )

        else:

            return AgentResult(
                success=False,
                agent_name=self.name,
                type="information",
                message=f"Acción meteorológica no soportada: {request.action}",
                data={}
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


        location_name = location.get("name")

        if location_name is None:
            location_name = "tu ubicación"

        return AgentResult(
    success=True,
    agent_name=self.name,
    type="information",
    message="Información meteorológica obtenida.",
    data={
        "weather": weather,
        "location": location
    },
    requires_llm=True
)