from core.models.request import AgentRequest

class InterpretationValidator:

    VALID_ACTIONS = {
        "conversation": {
            "chat"
        },

        "weather": {
            "current",
            "forecast"
        },

        "system": {
            "open_application",
            "close_application"
        },

        "news": {
            "search"
        },

        "memory": {
            "save",
            "get",
            "list",
            "delete"
        },

        "music": {
            "play",
            "pause",
            "next",
            "previous",
            "current",
            "volume",
            "search"
        },

        "astronomy": {
            "object",
            "sky"
        },

        "lacerta": {
            "agent_status",
            "enable_agent",
            "disable_agent"
        }
    }

    ALLOWED_PARAMETERS = {

        # =====================================
        # CONVERSATION
        # =====================================

        "conversation": {
            "chat": set()
        },

        # =====================================
        # WEATHER
        # =====================================

        "weather": {
            "current": {
                "location"
            },

            "forecast": {
                "location",
                "date"
            }
        },

        # =====================================
        # SYSTEM
        # =====================================

        "system": {
            "open_application": {
                "application"
            },

            "close_application": {
                "application"
            }
        },

        # =====================================
        # NEWS
        # =====================================

        "news": {
            "search": {
                "query",
                "date",
                "category"
            }
        },

        # =====================================
        # MEMORY
        # =====================================

        "memory": {
            "save": {
                "storage",
                "type",
                "key",
                "value",
                "category",
                "summary",
                "prompt"
            },

            "get": {
                "storage",
                "type",
                "key",
                "id"
            },

            "list": {
                "storage",
                "type",
                "category"
            },

            "delete": {
                "storage",
                "type",
                "key",
                "id"
            }
        },

        # =====================================
        # MUSIC
        # =====================================

        "music": {
            "play": {
                "song",
                "artist"
            },

            "pause": set(),

            "next": set(),

            "previous": set(),

            "current": set(),

            "volume": {
                "volume",
                "change"
            },

            "search": {
                "song",
                "artist"
            }
        },

        # =====================================
        # ASTRONOMY
        # =====================================

        "astronomy": {
            "object": {
                "object",
                "location",
                "date",
                "time"
            },

            "sky": {
                "location",
                "date",
                "time"
            }
        },

        # =====================================
        # LACERTA
        # =====================================

        "lacerta": {
            "agent_status": {
                "agent"
            },

            "enable_agent": {
                "agent"
            },

            "disable_agent": {
                "agent"
            }
        }
    }

    REQUIRED_PARAMETERS = {

        # SYSTEM
        ("system", "open_application"): {
            "application"
        },

        ("system", "close_application"): {
            "application"
        },

        # NEWS
        ("news", "search"): {
            "query"
        },

        # MEMORY
        ("memory", "save"): {
            "storage"
        },

        ("memory", "get"): {
            "storage"
        },

        ("memory", "list"): {
            "storage"
        },

        ("memory", "delete"): {
            "storage"
        },

        # LACERTA
        ("lacerta", "enable_agent"): {
            "agent"
        },

        ("lacerta", "disable_agent"): {
            "agent"
        },

        # ASTRONOMY
        ("astronomy", "object"): {
            "object"
        }
    }

    VALID_MEMORY_STORAGES = {
        "memory",
        "favorite"
    }

    VALID_WEATHER_DATES = {
        "today",
        "tomorrow",
        "day_after_tomorrow",
        "yesterday",
        "days_ago",
        "in_X_days",
        "in_X_hours",
        "X_hours_ago"
    }

    def validate(self, interpretation, text: str) -> bool:

        self._normalize(interpretation)

        # =========================
        # ROOT
        # =========================

        if not isinstance(interpretation.conversation, bool):
            return False

        if not isinstance(interpretation.planning_required, bool):
            return False

        # =========================
        # REQUESTS
        # =========================

        requests = interpretation.requests

        if not isinstance(requests, list):
            return False

        if not requests:
            return False

        # =========================
        # VALIDAR CADA REQUEST
        # =========================

        for request in requests:

            if not isinstance(request, AgentRequest):
                return False

            intent = request.intent
            action = request.action
            parameters = request.parameters
            context = request.context

            # =========================
            # INTENT
            # =========================

            if intent not in self.VALID_ACTIONS:
                return False

            # =========================
            # ACTION
            # =========================

            if action not in self.VALID_ACTIONS[intent]:
                return False

            # =========================
            # PARAMETERS
            # =========================

            if not isinstance(parameters, dict):
                return False

            if not self._validate_parameters(
                intent,
                action,
                parameters
            ):
                return False

            # =========================
            # CONTEXT
            # =========================

            if not self._validate_context(context):
                return False

            # =========================
            # LACERTA
            # =========================

            if intent == "lacerta":

                if "lacerta" not in text.lower():
                    return False

        return True

    # =========================================================
    # PARAMETERS
    # =========================================================

    def _validate_parameters(
        self,
        intent: str,
        action: str,
        parameters: dict
    ) -> bool:

        

        allowed = self.ALLOWED_PARAMETERS[intent][action]

        if not set(parameters.keys()).issubset(allowed):
            return False

        # =========================
        # MEMORY
        # =========================

        if intent == "memory":

            return self._validate_memory_parameters(
                action,
                parameters
            )

        # =========================
        # REQUIRED PARAMETERS
        # =========================

        required = self.REQUIRED_PARAMETERS.get(
            (intent, action),
            set()
        )

        if not required.issubset(parameters.keys()):
            return False

        # =========================
        # WEATHER DATE
        # =========================

        if intent == "weather":

            date = parameters.get("date")

            if date is not None:

                if not isinstance(date, str):
                    return False

                if date not in self.VALID_WEATHER_DATES:
                    return False

        # =========================
        # NEWS
        # =========================

        if intent == "news":

            query = parameters.get("query")

            if not isinstance(query, str):
                return False

            if not query.strip():
                return False

        # =========================
        # MUSIC VOLUME
        # =========================

        if intent == "music" and action == "volume":

            has_volume = "volume" in parameters
            has_change = "change" in parameters

            # Tiene que existir exactamente uno
            if has_volume == has_change:
                return False

        return True

    # =========================================================
    # MEMORY
    # =========================================================

    def _validate_memory_parameters(
        self,
        action: str,
        parameters: dict
    ) -> bool:

        storage = parameters.get("storage")

        # =========================
        # STORAGE
        # =========================

        if storage not in self.VALID_MEMORY_STORAGES:
            return False

        # =========================
        # NORMAL MEMORY
        # =========================

        if storage == "memory":

            allowed = {
                "storage",
                "type",
                "key",
                "value"
            }

            if not set(parameters.keys()).issubset(allowed):
                return False

            if action == "save":

                required = {
                    "storage",
                    "type",
                    "key",
                    "value"
                }

                return required.issubset(parameters.keys())

            if action == "get":

                required = {
                    "storage",
                    "type",
                    "key"
                }

                return required.issubset(parameters.keys())

            if action == "list":

                # type es opcional
                return True

            if action == "delete":

                required = {
                    "storage",
                    "type",
                    "key"
                }

                return required.issubset(parameters.keys())

        # =========================
        # FAVORITES
        # =========================

        if storage == "favorite":

            allowed = {
                "storage",
                "category",
                "summary",
                "prompt",
                "id"
            }

            if not set(parameters.keys()).issubset(allowed):
                return False

            if action == "save":

                required = {
                    "storage",
                    "category",
                    "summary",
                    "prompt"
                }

                return required.issubset(parameters.keys())

            if action == "get":

                required = {
                    "storage",
                    "id"
                }

                return required.issubset(parameters.keys())

            if action == "list":

                # category es opcional
                return True

            if action == "delete":

                required = {
                    "storage",
                    "id"
                }

                return required.issubset(parameters.keys())

        return False

    # =========================================================
    # CONTEXT
    # =========================================================

    def _validate_context(self, context) -> bool:

        if not isinstance(context, dict):
            return False

        if "used" not in context:
            return False

        if "request_id" not in context:
            return False

        if not isinstance(context["used"], bool):
            return False

        if context["used"]:

            if context["request_id"] is None:
                return False

        else:

            if context["request_id"] is not None:
                return False

        return True


    def _normalize(self, interpretation):

        # =========================================================
        # REQUESTS
        # =========================================================

        for request in interpretation.requests:

            # =========================
            # NEWS
            # =========================

            if request.intent == "news" and request.action == "search":

                parameters = request.parameters

                # topic → query
                if "topic" in parameters and "query" not in parameters:
                    parameters["query"] = parameters.pop("topic")

                # Defaults
                parameters.setdefault("date", "today")
                parameters.setdefault("category", "general")