import os
import requests
from datetime import date as date_class
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class NewsService:

    def __init__(self):

        self.api_key = os.getenv("GNEWS_API_KEY")

        self.url = "https://gnews.io/api/v4/search"

    def get_date_range(self, date: str | None):
    
        if not date:
            return None, None

        today = date_class.today()

    # =========================
    # Fechas relativas
    # =========================

        if date == "today":
            return today.isoformat(), today.isoformat()

        if date == "yesterday":
            yesterday = today - timedelta(days=1)
            return yesterday.isoformat(), yesterday.isoformat()

    # =========================
    # Año completo
    # =========================

        if len(date) == 4 and date.isdigit():

            year = int(date)

            return (
            f"{year}-01-01",
            f"{year}-12-31"
        )

        return None, None

    def search(
        self,
        query: str,
        date: str | None = None,
        category: str | None = None
        ) -> list:

        date_from, date_to = self.get_date_range(date)

        if not query:
            query = category or ""

        if not query:
            return []

        params = {
        "apikey": self.api_key,
        "q": query,
        "lang": "es",
        "max": 3
        }

        if date_from:
            params["from"] = date_from

        if date_to:
            params["to"] = date_to

        print("API key cargada:", bool(self.api_key))
        print(
        "Longitud API key:",
            len(self.api_key) if self.api_key else 0
        )

        print(
        "Parámetros:",
        {
            **params,
            "apikey": "***"
        }
        )

        response = requests.get(
            self.url,
            params=params
        )

        print(
        "URL FINAL:",
        response.url.replace(self.api_key, "***")
        )   

        print("STATUS GNEWS:", response.status_code)
        print("RESPUESTA GNEWS:", response.text)

        response.raise_for_status()

        data = response.json()

        articles = []

        for article in data.get("articles", []):

            articles.append({
            "title": article.get("title"),
            "url": article.get("url"),
            "source": article.get("source", {}).get("name")
        })

        return articles

    def __repr__(self):
        return "<NewsService>"