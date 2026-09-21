from abc import ABC, abstractmethod

from core.models.request import AgentRequest
from core.models.result import AgentResult


class BaseAgent(ABC):
    """
    Clase base para todos los agentes de Lacerta.

    Todo agente deberá heredar de esta clase e implementar
    los métodos abstractos definidos aquí.
    """

    def __init__(
        self,
        name: str,
        description: str,
        capabilities: list[str],
        priority: int = 0,
        enabled: bool = True
    ):

        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.priority = priority
        self.enabled = enabled

    @property
    def id(self) -> str:
        return self.name.lower().replace(" ", "_")

    @abstractmethod
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Indica si este agente puede encargarse de la petición.
        """
        pass

    @abstractmethod
    def execute(self, request: AgentRequest) -> AgentResult:
        """
        Ejecuta la petición y devuelve un resultado
        para el orquestador.
        """
        pass

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}"
            f"(id='{self.id}', "
            f"name='{self.name}', "
            f"enabled={self.enabled})>"
        )