from agents.base_agent import BaseAgent
from core.result import AgentResult


class Hermes(BaseAgent):
    """
    Primer agente de Lacerta.

    Agente experimental utilizado para probar
    el sistema de registro y orquestación.
    """

    def __init__(self):
        super().__init__(
            name="Hermes",
            description="Agente encargado de comunicación básica.",
            capabilities=[
                "conversation",
                "greetings"
            ],
            priority=1
        )

    def can_handle(self, request: str) -> bool:
        """
        Determina si Hermes puede responder a la petición.
        """

        greetings = [
            "hola",
            "buenas",
            "hey",
            "buenos dias",
            "buenas tardes"
        ]
        request = request.lower()

        return any(greeting in request for greeting in greetings)

    def execute(self, request: str) -> AgentResult:
        """
        Ejecuta la respuesta de Hermes.
        """

        return AgentResult(
        success=True,
        agent_name=self.name,
        message="Saludo detectado.",
        data={
            "response": "Hola, soy Hermes, el primer agente de Lacerta."
        }
    )