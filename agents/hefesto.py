from agents.base_agent import BaseAgent
from core.request import AgentRequest
from core.result import AgentResult
from services.system_services import SystemService
from services.application_service import ApplicationService


class Hefesto(BaseAgent):
    """
    Agente encargado de gestionar aplicaciones del sistema.
    """

    def __init__(self):

        super().__init__(
            name="Hefesto",
            description="Agente encargado de gestionar aplicaciones.",
            capabilities=[
                "system",
                "applications"
            ],
            priority=1
        )

        self.application_service = ApplicationService()
        self.system = SystemService()

    def can_handle(self, request: AgentRequest) -> bool:
        """
        Determina si Hefesto puede responder a la petición.
        """

        return (
            request.intent == "system"
            and request.action == "open_application"
        )

    def execute(self, request: AgentRequest) -> AgentResult:
        """
        Busca y abre la aplicación solicitada.
        """

        application_name = request.parameters.get("application")

        print(
            "Aplicación recibida:",
            repr(application_name)
        )

        if not application_name:

            return AgentResult(
                success=False,
                agent_name=self.name,
                type="action",
                message="No se indicó una aplicación.",
                data={
                    "response": (
                        "No me has indicado qué aplicación quieres abrir."
                    )
                }
            )

        # =====================================
        # Buscar aplicación
        # =====================================

        print(
            "Buscando aplicación:",
            application_name
        )

        application = self.application_service.find_application(
            application_name
        )

        print(
            "Resultado ApplicationService:",
            application
        )

        if application is None:

            return AgentResult(
                success=False,
                agent_name=self.name,
                type="action",
                message="Aplicación no encontrada.",
                data={
                    "response": (
                        f"No he encontrado la aplicación "
                        f"{application_name}."
                    )
                }
            )

        # =====================================
        # Abrir aplicación
        # =====================================

        opened = self.system.open_application(
            application["path"]
        )

        return AgentResult(
            success=opened,
            agent_name=self.name,
            type="action",
            message=(
                "Acción ejecutada."
                if opened
                else "Acción no ejecutada."
            ),
            data={
                "response": (
                    f"He abierto {application['name']}."
                    if opened
                    else (
                        f"No he podido abrir "
                        f"{application['name']}."
                    )
                )
            }
        )