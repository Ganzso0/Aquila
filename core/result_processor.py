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

        valid_results = []

        for result in results:

            if not result.success:
                continue

            valid_results.append(result)

        # =====================================
        # No hay resultados
        # =====================================

        if not valid_results:

            return "No se pudo generar una respuesta."

        # =====================================
        # Generar UNA respuesta con Zeus
        # =====================================

        return self._ai_service.generate_response(
            text,
            request,
            valid_results
        )

    def __repr__(self):
        return "<ResultProcessor>"