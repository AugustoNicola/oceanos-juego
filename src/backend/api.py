from fastapi import APIRouter, HTTPException
import uuid

from backend.estado import PARTIDAS, JUGADORES_ACTIVOS, LOCKS
from administrador.administrador_de_juego import AdministradorDeJuego
from jugador.DecisionesCacheadas.decisiones_cacheadas import JugadorDecisionesCacheadas
from administrador.acción import Acción
from juego.carta import Carta
from collections import Counter as Multiset

router = APIRouter()


@router.post("/crear_partida")
def crearPartida(request: dict):
    idPartida = str(uuid.uuid4())
    PARTIDAS[idPartida] = AdministradorDeJuego(
        request["jugadores"],
        verbosidad=AdministradorDeJuego.Verbosidad.OMNISCIENTE,
        partidaActiva=True
    )
    JUGADORES_ACTIVOS[idPartida] = request["posición_jugador_activo"]
    
    # comenzar partida, esperamos en ROBO
    partida = PARTIDAS[idPartida]
    partida.continuar()
    
    return {
        "id_partida": idPartida,
        "estado": partida.obtenerEstadoPartida()
    }

@router.post("/partida/{idPartida}/ok")
def ok(idPartida: str):
    partida = PARTIDAS.get(idPartida)
    if not partida:
        raise HTTPException(404, "Partida no encontrada")
    with LOCKS[idPartida]:
        partida.continuar()
        return {
            "id_partida": idPartida,
            "estado": partida.obtenerEstadoPartida()
        }

@router.post("/partida/{idPartida}/accion_robo")
def acciónRobo(idPartida: str, request: dict):
    partida = PARTIDAS.get(idPartida)
    if not partida:
        raise HTTPException(404, "Partida no encontrada")
    with LOCKS[idPartida]:
        if partida._juego.deQuiénEsTurno != JUGADORES_ACTIVOS[idPartida]:
            raise HTTPException(400, "¡No es tu turno!")
        if not partida._juego.hayQueRobar():
            raise HTTPException(400, "¡No es hora de robar!")
        
        # * cachear estado
        jugador: JugadorDecisionesCacheadas = partida._jugadores[JUGADORES_ACTIVOS[idPartida]]
        if request["acción_robo_elegida"] == "mazo":
            # robar del mazo
            jugador.acciónDeRobo = Acción.Robo.DEL_MAZO
            jugador.cartaARobarDelMazo = request["carta_elegida"]
            jugador.pilaDeDescarteDondeDescartarOtroRobo = request["pila_descarte_elegida"]
        elif request["acción_robo_elegida"] == "descarte":
            # robar del descarte
            jugador.acciónDeRobo = Acción.Robo.DEL_DESCARTE_0 if request["pila_descarte_robada"] == 0 else Acción.Robo.DEL_DESCARTE_1
        else:
            raise HTTPException(400, "¡Opción inválida!")
        
        # * continuar la partida, con decisiones ya elegidas
        partida.continuar()
        return {
            "id_partida": idPartida,
            "estado": partida.obtenerEstadoPartida()
        }

@router.post("/partida/{idPartida}/accion_duos")
def acciónDúos(idPartida: str, request: dict):
    partida = PARTIDAS.get(idPartida)
    if not partida:
        raise HTTPException(404, "Partida no encontrada")
    with LOCKS[idPartida]:
        if partida._juego.deQuiénEsTurno != JUGADORES_ACTIVOS[idPartida]:
            raise HTTPException(400, "¡No es tu turno!")
        if not partida._juego.seHaRobadoEsteTurno():
            raise HTTPException(400, "¡No es hora de jugar dúos!")
        
        # * cachear estado
        jugador: JugadorDecisionesCacheadas = partida._jugadores[JUGADORES_ACTIVOS[idPartida]]
        if request["acción_dúos_elegida"] == "no":
            # no jugar dúos
            jugador.acciónDeDúos = Acción.Dúos.NO_JUGAR
            jugador.cartasDeDúoAJugar = None
            jugador.parámetrosDeDúo = None
        else:
            # jugamos algún dúo
            jugador.cartasDeDúoAJugar = Multiset([
                Carta(request["cartas_jugadas"][0].tipo, request["cartas_jugadas"][0].color),
                Carta(request["cartas_jugadas"][1].tipo, request["cartas_jugadas"][1].color)
            ])
            if request["acción_dúos_elegida"] == "pez":
                # jugar dúo de peces
                jugador.acciónDeDúos = Acción.Dúos.JUGAR_PECES
                jugador.parámetrosDeDúo = None
            elif request["acción_dúos_elegida"] == "barco":
                # jugar dúo de barcos
                jugador.acciónDeDúos = Acción.Dúos.JUGAR_BARCOS
                jugador.parámetrosDeDúo = None
            elif request["acción_dúos_elegida"] == "cangrejo":
                # jugar dúo de cangrejos
                jugador.acciónDeDúos = Acción.Dúos.JUGAR_CANGREJOS
                jugador.parámetrosDeDúo = [request["pila_descarte_elegida"]]
                jugador.cartaElegidaParaRobarConDúoDeCangrejo = request["carta_descarte_robada"]
            elif request["acción_dúos_elegida"] == "nadador_tiburón":
                # jugar dúo de nadador y tiburón
                jugador.acciónDeDúos = Acción.Dúos.JUGAR_NADADOR_Y_TIBURÓN
                jugador.parámetrosDeDúo = [request["jugador_elegido"]]
            else:
                raise HTTPException(400, "¡Opción inválida!")
        
        # * continuar la partida, con decisiones ya elegidas
        partida.continuar()
        return {
            "id_partida": idPartida,
            "estado": partida.obtenerEstadoPartida()
        }

@router.post("/partida/{idPartida}/accion_fin")
def acciónFin(idPartida: str, request: dict):
    partida = PARTIDAS.get(idPartida)
    if not partida:
        raise HTTPException(404, "Partida no encontrada")
    with LOCKS[idPartida]:
        if partida._juego.deQuiénEsTurno != JUGADORES_ACTIVOS[idPartida]:
            raise HTTPException(400, "¡No es tu turno!")
        if partida._juego.hayQueTomarDecisionesDeRoboDelMazo() or not partida._juego.seHaRobadoEsteTurno():
            raise HTTPException(400, "¡No es hora de terminar el turno!")
        
        # * cachear estado
        jugador: JugadorDecisionesCacheadas = partida._jugadores[JUGADORES_ACTIVOS[idPartida]]
        if request["acción_fin_elegida"] == "pasar":
            # pasar de turno
            jugador.acciónDeFinDeTurno = Acción.FinDeTurno.PASAR_TURNO
        elif request["acción_fin_elegida"] == "basta":
            # decir ¡Basta!
            jugador.acciónDeFinDeTurno = Acción.FinDeTurno.DECIR_BASTA
        elif request["acción_fin_elegida"] == "última_chance":
            # decir ¡Última Chance!
            jugador.acciónDeFinDeTurno = Acción.FinDeTurno.DECIR_ÚLTIMA_CHANCE
        else:
            raise HTTPException(400, "¡Opción inválida!")
        
        # * continuar la partida, con decisiones ya elegidas
        partida.continuar()
        return {
            "id_partida": idPartida,
            "estado": partida.obtenerEstadoPartida()
        }