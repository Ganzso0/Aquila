from memory_service import MemoryService


memory = MemoryService()


# =====================================
# Guardar favoritos
# =====================================

favorite_id_1 = memory.save_favorite(
    "telescope",
    "Sky-Watcher 200P como posible próximo telescopio",
    "Quiero comprarme el Sky-Watcher 200P, guárdalo en favoritos."
)

favorite_id_2 = memory.save_favorite(
    "game",
    "Monster Hunter World",
    "Quiero jugar a Monster Hunter World, guárdalo en favoritos."
)


print("\n--- FAVORITOS GUARDADOS ---")
print("holas")

print("ID 1:", favorite_id_1)
print("ID 2:", favorite_id_2)


# =====================================
# Obtener un favorito
# =====================================

print("\n--- FAVORITO 1 ---")

print(
    memory.get_favorite(
        favorite_id_1
    )
)


# =====================================
# Obtener todos
# =====================================

print("\n--- TODOS LOS FAVORITOS ---")

print(
    memory.get_favorites()
)


# =====================================
# Filtrar por categoría
# =====================================

print("\n--- FAVORITOS: TELESCOPE ---")

print(
    memory.get_favorites(
        "telescope"
    )
)


# =====================================
# Eliminar favorito
# =====================================

print("\n--- ELIMINAR FAVORITO 1 ---")

print(
    memory.delete_favorite(
        favorite_id_1
    )
)


# =====================================
# Comprobar que ya no existe
# =====================================

print("\n--- COMPROBAR FAVORITO 1 ---")

print(
    memory.get_favorite(
        favorite_id_1
    )
)


# =====================================
# Comprobar favoritos restantes
# =====================================

print("\n--- FAVORITOS RESTANTES ---")

print(
    memory.get_favorites()
)