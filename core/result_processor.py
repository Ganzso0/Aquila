from core.result import AgentResult


class ResultProcessor:
    """
    Procesa los resultados devueltos por los agentes
    y genera una respuesta final para el usuario.
    """

    def __init__(self, ai_service):
        self._ai_service = ai_service

    def process(self, results: list[AgentResult]) -> str:
        """
        Combina los resultados de varios agentes.
        """

        responses = []

        for result in results:

            if not result.success:
                continue

            # Si el agente proporciona una respuesta directa,
            # la utilizamos.
            if "response" in result.data:
                responses.append(result.data["response"])
                continue

            # Si no hay respuesta directa, dejamos que Qwen
            # interprete el resultado.
            response = self._ai_service.generate_response(result)

            if response:
                responses.append(response)

        if not responses:
            return "No se pudo generar una respuesta."

        return "\n".join(responses)

    def __repr__(self):
        return "<ResultProcessor>"