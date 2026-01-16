from threading import Lock
from collections import defaultdict
from typing import Dict
from administrador.administrador_de_juego import AdministradorDeJuego

PARTIDAS: Dict[str, AdministradorDeJuego] = {}
JUGADORES_ACTIVOS: Dict[str, int] = {}
LOCKS = defaultdict(Lock)
