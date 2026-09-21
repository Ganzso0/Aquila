from datetime import datetime, timedelta
from core.models.request import AgentRequest


class CronosService:

    def __init__(self):
        pass

    def get_now(self) -> datetime:
        return datetime.now()

    def resolve(self, request: AgentRequest) -> AgentRequest:

        # Resolver request principal
        date_value = request.parameters.get("date")
        time_value = request.parameters.get("time")

        # Desplazamiento relativo:
        # "in_2_hours" / "2_hours_ago"
        if self.is_relative_time(time_value):

            resolved_datetime = self.resolve_relative_time(time_value)

            request.parameters["date"] = (
                resolved_datetime.date().isoformat()
            )

            request.parameters["time"] = (
                resolved_datetime.strftime("%H:%M:%S")
            )

        else:

            request.parameters["date"] = self.resolve_date(date_value)
            request.parameters["time"] = self.resolve_time(time_value)

        # Resolver subrequests
        for sub_request in request.requests:

            parameters = sub_request.get("parameters", {})

            sub_date = parameters.get("date")
            sub_time = parameters.get("time")

            if self.is_relative_time(sub_time):

                resolved_datetime = self.resolve_relative_time(sub_time)

                parameters["date"] = (
                    resolved_datetime.date().isoformat()
                )

                parameters["time"] = (
                    resolved_datetime.strftime("%H:%M:%S")
                )

            else:

                if sub_date is not None:
                    parameters["date"] = self.resolve_date(sub_date)

                if sub_time is not None:
                    parameters["time"] = self.resolve_time(sub_time)

        return request

    def resolve_date(self, date_value: str | None) -> str | None:

        if date_value is None:
            return None

        today = self.get_now().date()

        if date_value == "today":
            return today.isoformat()

        if date_value == "tomorrow":
            return (today + timedelta(days=1)).isoformat()

        if date_value == "yesterday":
            return (today - timedelta(days=1)).isoformat()

        if date_value == "day_after_tomorrow":
            return (today + timedelta(days=2)).isoformat()

        return date_value

    def resolve_time(self, time_value: str | None) -> str | None:

        if time_value is None:
            return None

        if time_value == "now":
            return self.get_now().strftime("%H:%M:%S")

        return time_value

    def is_relative_time(self, time_value: str | None) -> bool:

        if time_value is None:
            return False

        return (
            (time_value.startswith("in_") and time_value.endswith("_hours"))
            or
            time_value.endswith("_hours_ago")
        )

    def resolve_relative_time(self, time_value: str) -> datetime:

        now = self.get_now()

        if time_value.startswith("in_") and time_value.endswith("_hours"):

            hours = int(
                time_value.removeprefix("in_").removesuffix("_hours")
            )

            return now + timedelta(hours=hours)

        if time_value.endswith("_hours_ago"):

            hours = int(
                time_value.removesuffix("_hours_ago")
            )

            return now - timedelta(hours=hours)

        return now