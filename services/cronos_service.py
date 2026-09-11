from datetime import datetime, timedelta
from core.request import AgentRequest


class CronosService:

    def __init__(self):
        pass

    def resolve(self, request: AgentRequest) -> AgentRequest:

        # Resolver request principal
        date_value = request.parameters.get("date")

        request.parameters["date"] = self.resolve_date(date_value)

        # Resolver subrequests si existen
        for sub_request in request.requests:

            sub_date = sub_request.get("parameters", {}).get("date")

            if sub_date is not None:
                sub_request["parameters"]["date"] = self.resolve_date(
                    sub_date
                )

        return request

    def resolve_date(self, date_value: str | None) -> str | None:

        if date_value is None:
            return None

        today = datetime.now().date()

        if date_value == "today":
            return today.isoformat()

        if date_value == "tomorrow":
            return (today + timedelta(days=1)).isoformat()

        if date_value == "yesterday":
            return (today - timedelta(days=1)).isoformat()

        if date_value == "day_after_tomorrow":
            return (today + timedelta(days=2)).isoformat()

        return date_value