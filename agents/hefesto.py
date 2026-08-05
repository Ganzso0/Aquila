from agents.base_agent import BaseAgent
from core.result import AgentResult
from services.system_services import SystemService
from services.application_service import ApplicationService


class Hefesto(BaseAgent):
    """
    Primer agente de Lacerta.

    Agente experimental utilizado para probar
    el sistema de registro y orquestación.
    """

    def __init__(self):
        super().__init__(
            name="Hefesto",
            description="Agente encargado de comunicación básica.",
            capabilities=[
                "conversation",
                "greetings"
            ],
            priority=1
        )
        
        self.application_service = ApplicationService()
        self.system = SystemService()


    def can_handle(self, request: str) -> bool:
        """
        Determina si Hermes puede responder a la petición.
        """

        greetings = [
            "abre",
            
        ]
        request = request.lower()

        return any(greeting in request for greeting in greetings)

    def execute(self, request: str) -> AgentResult:
        """
        Ejecuta la respuesta de Hermes.
        """



        application = self.application_service.find_application(request)
        print(application)

        if application is None:

            return AgentResult(
        success=False,
        agent_name=self.name,
        type="action",
        message="Acción no ejecutada.",
        data={
            "response": "No he encontrado la aplicación."
        }
    )

        opened = self.system.open_application(
            application["path"]
        )

        return AgentResult(
    success=opened,
    agent_name=self.name,
    type="action",
    message="Acción ejecutada.",
    data={
        "response": (
            f"He abierto {application['name']}."
            if opened
            else f"No he podido abrir {application['name']}."
        )
    }
)