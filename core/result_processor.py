class ResultProcessor:
    """
    Procesa los resultados devueltos por los agentes
    y genera una respuesta final para el usuario.
    """

    def process(self, results: list) -> str:
        """
        Combina los resultados de varios agentes.
        """

        responses = []

        for result in results:

            if not result.success:
                continue

            if "response" in result.data:
                responses.append(result.data["response"])

        if not responses:
            return "No se pudo generar una respuesta."

        return "\n".join(responses)


    def __repr__(self):
        return "<ResultProcessor>"