from core.request import AgentRequest
from core.result import AgentResult
from memory.memory_service import MemoryService


class MemoryManager:

    def __init__(self, memory_service: MemoryService):

        self.memory_service = memory_service

    def execute(self, request: AgentRequest) -> AgentResult:

        action = request.action
        parameters = request.parameters

        # =====================================
        # MEMORIA
        # =====================================

        if request.intent == "memory":

            memory_type = parameters.get("type")
            key = parameters.get("key")
            value = parameters.get("value")

            if action == "save":

                if not memory_type or not key or not value:
                    return AgentResult(
                        success=False,
                        agent_name="MemoryManager",
                        type="memory",
                        message="Faltan datos para guardar la memoria.",
                        data={
                            "response": (
                                "Necesito el tipo, la clave y el valor "
                                "para guardar esa memoria."
                            )
                        },
                    )

                self.memory_service.save_memory(
                    memory_type,
                    key,
                    value
                )

                return AgentResult(
                    success=True,
                    agent_name="MemoryManager",
                    type="memory",
                    message="Memoria guardada correctamente.",
                    data={
                        "response": f"He guardado en memoria: {value}."
                    },
                )

            if action == "get":

                if not memory_type or not key:
                    return AgentResult(
                        success=False,
                        agent_name="MemoryManager",
                        type="memory",
                        message="Faltan datos para buscar la memoria.",
                        data={
                            "response": (
                                "Necesito saber qué memoria "
                                "quieres consultar."
                            )
                        },
                    )

                memory = self.memory_service.get_memory(
                    memory_type,
                    key
                )

                if memory is None:
                    return AgentResult(
                        success=False,
                        agent_name="MemoryManager",
                        type="memory",
                        message="Memoria no encontrada.",
                        data={
                            "response": (
                                "No tengo esa información "
                                "guardada en memoria."
                            )
                        },
                    )

                return AgentResult(
                    success=True,
                    agent_name="MemoryManager",
                    type="memory",
                    message="Memoria encontrada.",
                    data={
                        "memory": memory,
                        "response": memory["value"]
                    },
                )

            if action == "list":

                memories = self.memory_service.get_memories(
                    memory_type
                )

                return AgentResult(
                    success=True,
                    agent_name="MemoryManager",
                    type="memory",
                    message="Memorias recuperadas.",
                    data={
                        "memories": memories
                    },
                )

            if action == "delete":

                if not memory_type or not key:
                    return AgentResult(
                        success=False,
                        agent_name="MemoryManager",
                        type="memory",
                        message="Faltan datos para eliminar la memoria.",
                        data={
                            "response": (
                                "Necesito saber qué memoria "
                                "quieres eliminar."
                            )
                        },
                    )

                deleted = self.memory_service.delete_memory(
                    memory_type,
                    key
                )

                return AgentResult(
                    success=deleted,
                    agent_name="MemoryManager",
                    type="memory",
                    message=(
                        "Memoria eliminada."
                        if deleted
                        else "Memoria no encontrada."
                    ),
                    data={
                        "response": (
                            "He eliminado esa memoria."
                            if deleted
                            else "No he encontrado esa memoria para eliminarla."
                        )
                    },
                )

        # =====================================
        # FAVORITOS
        # =====================================

        if request.intent == "favorites":

            category = parameters.get("category")
            summary = parameters.get("summary")
            prompt = parameters.get("prompt")

            if action == "save":

                if not category or not summary or not prompt:
                    return AgentResult(
                        success=False,
                        agent_name="MemoryManager",
                        type="favorite",
                        message="Faltan datos para guardar el favorito.",
                        data={
                            "response": (
                                "Necesito la categoría, el resumen "
                                "y la petición para guardar el favorito."
                            )
                        },
                    )

                favorite_id = self.memory_service.save_favorite(
                    category,
                    summary,
                    prompt
                )

                return AgentResult(
                    success=True,
                    agent_name="MemoryManager",
                    type="favorite",
                    message="Favorito guardado correctamente.",
                    data={
                        "favorite_id": favorite_id,
                        "response": (
                            "He guardado ese elemento en favoritos."
                        ),
                    },
                )

            if action == "get":

                favorite_id = parameters.get("id")

                if not favorite_id:
                    return AgentResult(
                        success=False,
                        agent_name="MemoryManager",
                        type="favorite",
                        message="Falta el ID del favorito.",
                        data={
                            "response": (
                                "Necesito saber qué favorito "
                                "quieres consultar."
                            )
                        },
                    )

                favorite = self.memory_service.get_favorite(
                    favorite_id
                )

                if favorite is None:
                    return AgentResult(
                        success=False,
                        agent_name="MemoryManager",
                        type="favorite",
                        message="Favorito no encontrado.",
                        data={
                            "response": (
                                "No he encontrado ese favorito."
                            )
                        },
                    )

                return AgentResult(
                    success=True,
                    agent_name="MemoryManager",
                    type="favorite",
                    message="Favorito encontrado.",
                    data={
                        "favorite": favorite,
                        "response": favorite["summary"]
                    },
                )

            if action == "list":

                favorites = self.memory_service.get_favorites(
                    category
                )

                return AgentResult(
                    success=True,
                    agent_name="MemoryManager",
                    type="favorite",
                    message="Favoritos recuperados.",
                    data={
                        "favorites": favorites
                    },
                )

            if action == "delete":

                favorite_id = parameters.get("id")

                if not favorite_id:
                    return AgentResult(
                        success=False,
                        agent_name="MemoryManager",
                        type="favorite",
                        message="Falta el ID del favorito.",
                        data={
                            "response": (
                                "Necesito saber qué favorito "
                                "quieres eliminar."
                            )
                        },
                    )

                deleted = self.memory_service.delete_favorite(
                    favorite_id
                )

                return AgentResult(
                    success=deleted,
                    agent_name="MemoryManager",
                    type="favorite",
                    message=(
                        "Favorito eliminado."
                        if deleted
                        else "Favorito no encontrado."
                    ),
                    data={
                        "response": (
                            "He eliminado ese favorito."
                            if deleted
                            else "No he encontrado ese favorito."
                        )
                    },
                )

        # =====================================
        # ACCIÓN DESCONOCIDA
        # =====================================

        return AgentResult(
            success=False,
            agent_name="MemoryManager",
            type="memory",
            message="Acción de memoria no soportada.",
            data={
                "response": (
                    f"No puedo realizar la acción "
                    f"{action} sobre la memoria."
                )
            },
        )