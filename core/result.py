class AgentResult:
    """
    Resultado devuelto por un agente de Lacerta.

    Contiene la información que el agente devuelve
    al orquestador después de procesar una tarea.
    """

    def __init__(
        self,
        success: bool,
        agent_name: str,
        type:str,
        message: str,
        data: dict | None = None
    ):
        self.success = success
        self.agent_name = agent_name
        self.type = type
        self.message = message
        self.data = data or {}

    def __repr__(self):
        return (
            f"<AgentResult("
            f"agent='{self.agent_name}', "
            f"success={self.success}"
            f")>"
        )