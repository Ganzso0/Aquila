from agents.base_agent import BaseAgent
from core.request import AgentRequest
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

    def can_handle(self, request: AgentRequest) -> bool:
        """
        Determina si Hermes puede responder a la petición.
        """

        return (
            request.intent == "conversation"
            and request.action in [
                "chat",
                "greeting"
            ]
        )

    def execute(self, request: AgentRequest) -> AgentResult:
        """
        Ejecuta la petición de conversación.
        """

        return AgentResult(
            success=True,
            agent_name=self.name,
            type="conversation",
            message="Conversación procesada.",
            data={
                "type": "greeting",
                "agent": "Hermes",
                "greeting": True
            }
        )