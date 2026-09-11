import base64
import hashlib
import json
import secrets
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlencode, urlparse, parse_qs

import requests

from core.result import AgentResult

import os
from dotenv import load_dotenv

from pathlib import Path

load_dotenv()



class SpotifyService:

    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    REDIRECT_URI = os.getenv(
        "SPOTIFY_REDIRECT_URI")
    

    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    API_URL = "https://api.spotify.com/v1"

    SCOPES = [
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
    ]

    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.expires_at = 0

        self.token_file = Path("memory/spotify_token.json")

        self._load_token()



    def _load_token(self):
            if not self.token_file.exists():
                return

            try:
                with open(self.token_file, "r", encoding="utf-8") as f:
                    token_data = json.load(f)

                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                self.expires_at = token_data.get("expires_at", 0)

                print("Token de Spotify cargado.")

            except (json.JSONDecodeError, OSError):
                print("No se pudo cargar el token de Spotify.")


    def _save_token(self):
        self.token_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        token_data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at
        }

        with open(self.token_file, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=4)


    def _refresh_access_token(self):
        print("Renovando token de Spotify...")

        response = requests.post(
            self.TOKEN_URL,
            data={
            "client_id": self.CLIENT_ID,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            },
        )

        response.raise_for_status()

        token_data = response.json()

        self.access_token = token_data["access_token"]

        # Spotify puede no devolver un nuevo refresh_token.
        if "refresh_token" in token_data:
            self.refresh_token = token_data["refresh_token"]

        self.expires_at = (
            time.time()
            + token_data["expires_in"]
        )

        self._save_token()

        print("Token de Spotify renovado.")

    def authenticate(self):
        """
        Realiza la autenticación OAuth 2.0 con PKCE.
        """

        verifier = self._generate_code_verifier()

        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(
                verifier.encode("utf-8")
            ).digest()
        ).decode("utf-8").rstrip("=")

        state = secrets.token_urlsafe(16)

        params = {
            "client_id": self.CLIENT_ID,
            "response_type": "code",
            "redirect_uri": self.REDIRECT_URI,
            "scope": " ".join(self.SCOPES),
            "code_challenge_method": "S256",
            "code_challenge": challenge,
            "state": state,
        }

        auth_url = (
            f"{self.AUTH_URL}?"
            f"{urlencode(params)}"
        )

       

        print("Abriendo Spotify para autorizar Lacerta...")

        callback_result = {}

        class CallbackHandler(BaseHTTPRequestHandler):

            def do_GET(self):
                query = parse_qs(
                    urlparse(self.path).query
                )

                callback_result["code"] = query.get(
                    "code",
                    [None]
                )[0]

                callback_result["state"] = query.get(
                    "state",
                    [None]
                )[0]

                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "text/html; charset=utf-8"
                )
                self.end_headers()

                self.wfile.write(
                    b"""
                    <html>
                    <body>
                    <h2>Lacerta conectado con Spotify.</h2>
                    <p>Ya puedes cerrar esta ventana.</p>
                    </body>
                    </html>
                    """
                )

        server = HTTPServer(
            ("127.0.0.1", 8888),
            CallbackHandler
        )

        thread = threading.Thread(
            target=server.handle_request
        )

        thread.start()

        webbrowser.open(auth_url)

        thread.join()

        server.server_close()

        if callback_result.get("state") != state:
            raise RuntimeError(
                "El estado OAuth no coincide."
            )

        code = callback_result.get("code")

        if not code:
            raise RuntimeError(
                "Spotify no devolvió un código de autorización."
            )

        response = requests.post(
            self.TOKEN_URL,
            data={
                "client_id": self.CLIENT_ID,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.REDIRECT_URI,
                "code_verifier": verifier,
            },
        )

        response.raise_for_status()

        token_data = response.json()

        self.access_token = token_data["access_token"]
        self.refresh_token = token_data.get("refresh_token")

        self.expires_at = (
            time.time()
            + token_data["expires_in"]
        )

        self._save_token()

        print("Spotify autenticado correctamente.")

    def _generate_code_verifier(self) -> str:
        return secrets.token_urlsafe(64)

    def _ensure_authenticated(self):

        # Tenemos un access token todavía válido
        if (
                self.access_token
                and time.time() < self.expires_at - 60
            ):
                return

        # El access token ha caducado pero tenemos refresh token
        if self.refresh_token:
            self._refresh_access_token()
            return

        # No tenemos ningún token
        self.authenticate()

    def _headers(self):
        self._ensure_authenticated()

        return {
            "Authorization":
                f"Bearer {self.access_token}"
        }

    def play(self, song=None, artist=None) -> AgentResult:
        self._ensure_authenticated()

    # Si se ha pedido una canción o un artista concreto,
    # buscamos antes de reproducir.
        if song or artist:

            if song and artist:
                query = f"track:{song} artist:{artist}"
            elif song:
                query = f"track:{song}"
            else:
                query = f"artist:{artist}"

            search_result = self.search_track(query)

            if not search_result.success:
                return search_result

            results = search_result.data.get("results", [])

            if not results:
                return AgentResult(
                    success=False,
                    agent_name="Orfeo",
                    type="error",
                    message="No se encontró ninguna canción.",
                    data={
                        "response": "No encontré ninguna canción para reproducir."
                    }
                )

            first = results[0]

            return self.play_uri(first["uri"])

    # Si no se especificó canción ni artista,
    # simplemente reanudamos la reproducción.
        response = requests.put(
            f"{self.API_URL}/me/player/play",
            headers=self._headers()
        )

        if not response.ok:
            print("Spotify error:", response.status_code)
            print("Spotify response:", response.text)

        response.raise_for_status()

        return AgentResult(
            success=True,
            agent_name="Orfeo",
            type="action",
            message="Reproducción iniciada.",
            data={
            "response": "Reproducción iniciada."
            }
        )

    def play_uri(self, uri: str) -> AgentResult:
        self._ensure_authenticated()

        response = requests.put(
            f"{self.API_URL}/me/player/play",
            headers=self._headers(),
            json={
            "uris": [uri]
            } 
        )

        response.raise_for_status()

        return AgentResult(
            success=True,
            agent_name="Orfeo",
            type="action",
            message="Reproducción iniciada.",
            data={
            "response": "Reproducción iniciada."
            }
        )

    def pause(self) -> AgentResult:
        self._ensure_authenticated()

        response = requests.put(
            f"{self.API_URL}/me/player/pause",
            headers=self._headers()
        )

        response.raise_for_status()

        return AgentResult(
            success=True,
            agent_name="Orfeo",
            type="action",
            message="Reproducción pausada.",
            data={
                "response": "Reproducción pausada."
            }
        )

    def next(self) -> AgentResult:
        self._ensure_authenticated()

        response = requests.post(
            f"{self.API_URL}/me/player/next",
            headers=self._headers()
        )

        response.raise_for_status()

        return AgentResult(
            success=True,
            agent_name="Orfeo",
            type="action",
            message="Siguiente canción.",
            data={
                "response": "Pasando a la siguiente canción."
            }
        )

    def previous(self) -> AgentResult:
        self._ensure_authenticated()

        response = requests.post(
            f"{self.API_URL}/me/player/previous",
            headers=self._headers()
        )

        response.raise_for_status()

        return AgentResult(
            success=True,
            agent_name="Orfeo",
            type="action",
            message="Canción anterior.",
            data={
                "response": "Volviendo a la canción anterior."
            }
        )
    def get_volume(self):
        self._ensure_authenticated()

        response = requests.get(
        f"{self.API_URL}/me/player",
        headers=self._headers()
        )

        response.raise_for_status()

        data = response.json()

        device = data.get("device")

        if not device:
            return None

        return device.get("volume_percent")

    def set_volume(self, volume: int) -> AgentResult:
        self._ensure_authenticated()

        volume = max(0, min(100, volume))

        response = requests.put(
            f"{self.API_URL}/me/player/volume",
            headers=self._headers(),
            params={
            "volume_percent": volume
        }
    )

        response.raise_for_status()

        return AgentResult(
            success=True,
            agent_name="Orfeo",
            type="action",
            message=f"Volumen ajustado al {volume}%.",
            data={
            "response": f"Volumen ajustado al {volume}%."
        }
    )

    def get_current_track(self) -> AgentResult:
        self._ensure_authenticated()

        response = requests.get(
            f"{self.API_URL}/me/player/currently-playing",
            headers=self._headers()
        )

        if response.status_code == 204:
            return AgentResult(
                success=False,
                agent_name="Orfeo",
                type="error",
                message="No hay ninguna canción reproduciéndose.",
                data={
                "response": "No hay ninguna canción reproduciéndose."
                }
            )

        response.raise_for_status()

        data = response.json()

        item = data.get("item")

        if not item:
            return AgentResult(
                success=False,
                agent_name="Orfeo",
                type="error",
                message="No se pudo obtener la canción actual.",
                data={
                "response": "No puedo saber qué canción está sonando."
                }
            )

        track_name = item.get("name")

        artists = item.get("artists", [])
        artist_names = ", ".join(
            artist.get("name", "")
            for artist in artists
        )

        album = item.get("album", {})
        album_name = album.get("name")

        return AgentResult(
            success=True,
            agent_name="Orfeo",
            type="music",
            message=f"Está sonando {track_name} de {artist_names}.",
            data={
                "track": track_name,
                "artist": artist_names,
                "album": album_name,
                "response": f"Está sonando {track_name} de {artist_names}."
            }
        )

    def search_track(self, query: str) -> AgentResult:
        self._ensure_authenticated()

        response = requests.get(
            f"{self.API_URL}/search",
            headers=self._headers(),
            params={
            "q": query,
            "type": "track",
            "limit": 5
            }
        )

        response.raise_for_status()

        data = response.json()

        tracks = data.get("tracks", {}).get("items", [])

        if not tracks:
            return AgentResult(
                success=False,
                agent_name="Orfeo",
                type="error",
                message=f"No se encontraron canciones para '{query}'.",
                data={
                    "response": f"No encontré ninguna canción para '{query}'."
                }
            )

        results = []

        for track in tracks:
            artists = ", ".join(
                artist.get("name", "")
                for artist in track.get("artists", [])
            )

            results.append({
                "name": track.get("name"),
                "artist": artists,
                "album": track.get("album", {}).get("name"),
                "uri": track.get("uri")
            })

        first = results[0]

        return AgentResult(
            success=True,
            agent_name="Orfeo",
            type="search",
            message=f"He encontrado '{first['name']}' de {first['artist']}.",
            data={
            "query": query,
            "results": results,
            "response": (
                f"He encontrado '{first['name']}' "
                f"de {first['artist']}."
            )
        }
    )
    def get_player_info(self):
        self._ensure_authenticated()

        response = requests.get(
            f"{self.API_URL}/me/player",
            headers=self._headers()
        )

        print("PLAYER STATUS:", response.status_code)
        print("PLAYER DATA:", response.json())

     