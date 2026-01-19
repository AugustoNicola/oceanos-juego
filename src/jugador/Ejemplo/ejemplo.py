from collections import Counter as Multiset
from administrador.acción import Acción
from juego.carta import Carta
from juego.partida import PartidaDeOcéanos
from administrador.evento import Evento
from ..base import JugadorBase
from jugador.registro import registrarComo

@registrarComo("CAMBIAR_ESTE_NOMBRE")
class EjemploDeBot(JugadorBase):
	# ========================= INTERFAZ DE JUEGO =========================
	def __init__(self) -> None:
		super().__init__()
		#* Acá se pueden hacer más cosas, como definir variables del Jugador
	
	def configurarParaJuego(self, juego: PartidaDeOcéanos, númeroDeJugador: int, listaDeEventos: list[Evento]) -> None:
		super().configurarParaJuego(juego, númeroDeJugador, listaDeEventos)
		#* Acá se pueden hacer más cosas, como cambiar el comportamiento según el número de jugadores
	
	def decidirAcciónDeRobo(self) -> Acción.Robo:
		# !Implementar y borrar la línea de abajo! 
		raise Exception("¡Implementame!")
	
	def decidirCómoRobarDelMazo(self, opcionesDeRobo: list[Carta]) -> tuple[int, int|None]:
		# !Implementar y borrar la línea de abajo! 
		raise Exception("¡Implementame!")
	
	def decidirAcciónDeDúos(self) -> tuple[Acción.Dúos, Multiset[Carta]|None, tuple[any]|None]:
		# !Implementar y borrar la línea de abajo! 
		raise Exception("¡Implementame!")
	
	def decidirQuéRobarConDúoDeCangrejos(self, descarteElegido: list[Carta]) -> int:
		# !Implementar y borrar la línea de abajo! 
		raise Exception("¡Implementame!")
	
	def decidirAcciónDeFinDeTurno(self) -> Acción.FinDeTurno:
		# !Implementar y borrar la línea de abajo! 
		raise Exception("¡Implementame!")
	
	def configurarInicioDeRonda(self, cartasInicialesDelDescarte: tuple[Carta, Carta]) -> None:
		# !Implementar y borrar la línea de abajo! 
		raise Exception("¡Implementame!")
	
	def configurarFinDeRonda(self, manos: list[Multiset[Carta]], puntajesDeRonda: list[int]) -> None:
		# !Implementar y borrar la línea de abajo! 
		raise Exception("¡Implementame!")
	
	def configurarInicioDeTurno(self) -> None:
		# !Implementar y borrar la línea de abajo! 
		raise Exception("¡Implementame!")
	
	# ============================ AUXILIARES =============================
	#* Acá se pueden definir más auxiliares para ser usados por tu Jugador!
	def miAuxiliarFachero(self, soyFachero: bool) -> str:
		if soyFachero:
			return "Soy fachero!"
		else:
			return "No soy tan fachero..."