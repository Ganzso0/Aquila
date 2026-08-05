from agents.base_agent import BaseAgent
from core.result import AgentResult


class Poseidon(BaseAgent):
    """
    Primer agente de Lacerta.

    Agente experimental utilizado para probar
    el sistema de registro y orquestación.
    """

    def __init__(self):
        super().__init__(
            name="Poseidon",
            description="Agente encargado de clima.",
            capabilities=[
                "conversation",
                "greetings"
            ],
            priority=1
        )

    def can_handle(self, request: str) -> bool:
        """
        Determina si Poseidon puede responder a la petición.
        """

        greetings = [
            "tiempo",
            "clima"
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
        type="information",
        message="Saludo detectado.",
        data={
            "response": "Hola, soy Poseidon, hacen 25 grados fuera"
        }
    )