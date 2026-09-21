from core.execution.registry import Registry
from agents.Hermes.hermes import Hermes
from agents.Poseidon.poseidon import Poseidon
from agents.Hefesto.hefesto import Hefesto
from agents.Orfeo.orfeo import Orfeo
from agents.Nix.nix import Nix


def load_agents(registry: Registry) -> None:
    """
    Carga y registra todos los agentes disponibles en Lacerta.
    """

    registry.register(Hermes())
    registry.register(Poseidon())
    registry.register(Hefesto())
    registry.register(Orfeo())
    registry.register(Nix())