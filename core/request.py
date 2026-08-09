class AgentRequest:
    """
    Petición estructurada generada por Zeus
    para ser procesada por un agente.
    """

    def __init__(
        self,
        intent: str,
        action: str,
        parameters: dict | None = None,
        context: dict | None = None
    ):
        self.intent = intent
        self.action = action
        self.parameters = parameters or {}
        self.context = context or {}