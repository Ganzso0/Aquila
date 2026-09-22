from core.models.result import AgentResult
from core.models.interpretation_result import InterpretationResult


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
        interpretation: InterpretationResult,
        results: list[AgentResult],
        history: list[dict]
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
        # Generar UNA respuesta con Logos
        # =====================================

        return self._ai_service.generate_response(
            text,
            interpretation,
            valid_results,
            history
        )

    def __repr__(self):
        return "<ResultProcessor>"