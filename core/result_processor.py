from core.result import AgentResult
from core.request import AgentRequest


class ResultProcessor:
    """
    Procesa los resultados devueltos por los agentes
    y genera una respuesta final para el usuario.
    """

    def __init__(self, ai_service):
        self._ai_service = ai_service

    def process(
        self,
        text: str,
        request: AgentRequest,
        results: list[AgentResult]
    ) -> str:

        responses = []

        for result in results:

            if not result.success:
                continue

            if result.requires_llm:

                response = self._ai_service.generate_response(
                    text,
                    request,
                    result
                )

                if response:
                    responses.append(response)

                continue

            if "response" in result.data:

                responses.append(
                    result.data["response"]
                )

        if not responses:
            return "No se pudo generar una respuesta."

        return "\n".join(responses)

    def __repr__(self):
        return "<ResultProcessor>"