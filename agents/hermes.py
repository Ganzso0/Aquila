from agents.base_agent import BaseAgent
from core.request import AgentRequest
from core.result import AgentResult
from services.news_service import NewsService

class Hermes(BaseAgent):
    """
    Agente encargado de proporcionar información de noticias.
    """


    def __init__(self):

        self.news = NewsService()

        super().__init__(
            name="Hermes",
            description="Agente encargado de noticias.",
            capabilities=[
            "news"
            ],
            priority=1
    )

    def can_handle(self, request: AgentRequest) -> bool:
        """
            Determina si Hermes puede responder a la petición.
        """

        return (
        request.intent == "news"
        and request.action == "search"
    )

    def execute(self, request: AgentRequest) -> AgentResult:
        """
        Ejecuta la petición de noticias.
        """

        query = request.parameters.get("query")
        date = request.parameters.get("date")
        category = request.parameters.get("category")

        print("Consulta recibida:", repr(query))
        print("Fecha recibida:", repr(date))
        print("Categoría recibida:", repr(category))

    # =====================================
    # Buscar noticias
    # =====================================

        print("Consultando NewsService...")
        articles = self.news.search(
         query=query,
           date=date,
             category=category 
             ) 
        print("Noticias encontradas:", len(articles))

    # =====================================
    # Comprobar resultado
    # =====================================

        if not articles:

            return AgentResult(
            success=False,
            agent_name=self.name,
            type="news",
            message="No se encontraron noticias.",
            data={
                "query": query,
                "date": date,
                "category": category
            },
            requires_llm=True
        )

    # =====================================
    # Preparar noticias para Zeus
    # =====================================

        news_for_llm = []

        for article in articles:

            news_for_llm.append({
            "title": article.get("title"),
            "description": article.get("description"),
            "source": article.get("source"),
            "published": article.get("published"),
            "url": article.get("url")
        })

    # =====================================
    # Devolver resultado
    # =====================================

        return AgentResult(
        success=True,
        agent_name=self.name,
        type="news",
        message="Noticias obtenidas correctamente.",
        data={
            "query": query,
            "date": date,
            "category": category,
            "articles": news_for_llm
        },
        requires_llm=True
    )

