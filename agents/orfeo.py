from agents.base_agent import BaseAgent
from core.request import AgentRequest
from core.result import AgentResult
from services.spotify_service import SpotifyService


class Orfeo(BaseAgent):
    """
    Agente encargado de controlar Spotify.
    """

    def __init__(self):
        super().__init__(
            name="Orfeo",
            description="Agente encargado de controlar Spotify.",
            capabilities=["music"],
            priority=1
        )

        self.spotify = SpotifyService()

    def can_handle(self, request: AgentRequest) -> bool:
        return request.intent == "music"

    def execute(self, request: AgentRequest) -> AgentResult:

        self.spotify.get_player_info()

        action = request.action

        if action == "play":

            song = request.parameters.get("song")
            artist = request.parameters.get("artist")

            return self.spotify.play(song, artist)

        elif action == "pause":
            return self.spotify.pause()

        elif action == "next":
            return self.spotify.next()

        elif action == "previous":
            return self.spotify.previous()

        elif action == "current":
            return self.spotify.get_current_track()

        elif action == "volume":

            volume = request.parameters.get("volume")
            change = request.parameters.get("change")

            if volume is not None:
                return self.spotify.set_volume(volume)

            if change is not None:
                current_volume = self.spotify.get_volume()

                if current_volume is None:
                    return AgentResult(
                        success=False,
                        agent_name=self.name,
                        type="error",
                        message="No hay un dispositivo Spotify activo.",
                        data={
                    "response": "No encuentro un dispositivo Spotify activo."
                        }
                    )

                new_volume = current_volume + change

                return self.spotify.set_volume(new_volume)

            return AgentResult(
                success=False,
                agent_name=self.name,
                type="error",
                message="No se especificó el volumen.",
                data={
            "response": "No sé a qué volumen quieres ponerlo."
                }
            )

        elif action == "search":

            query = request.parameters.get("query")
            artist = request.parameters.get("artist")

            if query:
                search_query = query
            elif artist:
                search_query = artist
            else:
                return AgentResult(
                    success=False,
                    agent_name=self.name,
                    type="error",
                    message="No se especificó qué buscar.",
                    data={
                        "response": "No sé qué canción quieres buscar."
                    }
                )

            return self.spotify.search_track(search_query)

        # elif action == "debug":
        #     self.spotify.get_player_info()

        #     return AgentResult(
        #         success=True,
        #         agent_name=self.name,
        #         type="debug",
        #         message="Información del reproductor obtenida.",
        #         data={
        #             "response": "Debug ejecutado."
        #         }
        #     )

        return AgentResult(
            success=False,
            agent_name=self.name,
            type="error",
            message=f"Acción de música no soportada: {action}",
            data={
                "response": f"No conozco la acción de música '{action}'."
            }
        )

    