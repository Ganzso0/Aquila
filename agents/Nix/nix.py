from agents.base_agent import BaseAgent
from core.models.request import AgentRequest
from core.models.result import AgentResult
from services.external.location_service import LocationService
from services.external.astronomy_service import AstronomyService


class Nix(BaseAgent):
    """
    Agente encargado de proporcionar información astronómica.
    """

    def __init__(self):

        super().__init__(
            name="Nix",
            description="Agente encargado de astronomía y observación del cielo.",
            capabilities=[
                "astronomy"
            ],
            priority=1
        )

        self.astronomy = AstronomyService()
        self.location = LocationService()

    def can_handle(self, request: AgentRequest) -> bool:
        return request.intent == "astronomy"

    def execute(self, request: AgentRequest) -> AgentResult:

        place = request.parameters.get("location")

        if place is not None:
            location = self.location.get_location(place)
        else:
            location = self.location.get_device_location()

        if location is None:
            return AgentResult(
                success=False,
                agent_name=self.name,
                type="information",
                message="No se pudo obtener la ubicación.",
                data={
                    "response": "No he podido determinar tu ubicación."
                }
            )

        action = request.action

        date = request.parameters.get("date")
        time = request.parameters.get("time")

        if action == "current_sky":

            data = self.astronomy.get_current_sky(
                location["latitude"],
                location["longitude"],
                date,
                time
            )

        elif (action == "object" or action =="sky" ):

            object_name = request.parameters.get("object")

            data = self.astronomy.get_object(
                object_name,
                location["latitude"],
                location["longitude"],
                date,
                time
            )

        else:

            return AgentResult(
                success=False,
                agent_name=self.name,
                type="error",
                message=f"Acción astronómica no soportada: {action}",
                data={
                    "response": (
                        f"No conozco la acción astronómica '{action}'."
                    )
                }
            )

        if data is None:
            return AgentResult(
                success=False,
                agent_name=self.name,
                type="information",
                message="No se pudo obtener información astronómica.",
                data={
                    "response": (
                        "No he podido obtener la información astronómica."
                    )
                }
            )

        return AgentResult(
            success=True,
            agent_name=self.name,
            type="information",
            message="Información astronómica obtenida.",
            data={
                "astronomy": data,
                "location": location
            },
            requires_llm=True
        )