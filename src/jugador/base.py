from collections import Counter as Multiset
from administrador.acción import Acción
from juego.carta import Carta
from juego.partida import PartidaDeOcéanos, cartasDelJuego
from administrador.evento import Evento
from enum import Enum

class JugadorBase():
	# =====================================================================
	# ========================= INTERFAZ DE JUEGO =========================
	# =====================================================================
	def __init__(self) -> None:
		self._juego: PartidaDeOcéanos = None
		self._númeroDeJugador: int = None
		self._listaDeEventos: list[Evento]
	
	def configurarParaJuego(self, juego: PartidaDeOcéanos, númeroDeJugador: int, listaDeEventos: list[Evento]) -> None:
		self._juego = juego
		self._númeroDeJugador = númeroDeJugador
		self._listaDeEventos = listaDeEventos
	
	def decidirAcciónDeRobo(self) -> Acción.Robo:
		raise Exception("¡Implementame!")
	
	def decidirCómoRobarDelMazo(self, opcionesDeRobo: list[Carta]) -> tuple[int, int|None]:
		raise Exception("¡Implementame!")
	
	def decidirAcciónDeDúos(self) -> tuple[Acción.Dúos, Multiset[Carta]|None, tuple[any]|None]:
		raise Exception("¡Implementame!")
	
	def decidirQuéRobarConDúoDeCangrejos(self, descarteElegido: list[Carta]) -> int:
		raise Exception("¡Implementame!")
	
	def decidirAcciónDeFinDeTurno(self) -> Acción.FinDeTurno:
		raise Exception("¡Implementame!")
	
	def configurarInicioDeRonda(self, cartasInicialesDelDescarte: tuple[Carta, Carta]) -> None:
		raise Exception("¡Implementame!")
	
	def configurarFinDeRonda(self, manos: list[Multiset[Carta]], puntajesDeRonda: list[int]) -> None:
		raise Exception("¡Implementame!")
	
	def configurarInicioDeTurno(self) -> None:
		raise Exception("¡Implementame!")
	
	# =====================================================================
	# ============================ AUXILIARES =============================
	# =====================================================================
	class Zona(Enum):
		"""
		Este enum se usa para poder expresar dónde se quiere buscar cartas que cumplan con alguna propiedad en los métodos de más abajo.
		"""
		MI_MANO       = "MI_MANO"        # Buscar únicamente en mi mano
		MI_ZONA_DÚOS  = "MI_ZONA_DÚOS"   # Buscar únicamente en mi zona de dúos
		TODO_MÍO      = "TODO_MÍO"       # Buscar en mi mano y en mi zona de dúos
		TODO_EL_JUEGO = "TODO_EL_JUEGO"  # Buscar en `cartasDelJuego` (es decir, las 56 cartas de todo el juego)
	
	# ------------------------ Buscar y filtrar cartas -------------------------
	def _cantidadDeCartasQueCumplenEn(self, propiedadBuscada, zonaABuscar: Zona):
		"""
		Devuelve la cantidad de cartas que cumplen una condición en la Zona indicada (ver `JugadorBase.Zona`)
		"""
		total = 0
		
		if zonaABuscar in [JugadorBase.Zona.MI_MANO, JugadorBase.Zona.TODO_MÍO]:
			# Buscamos en la mano del jugador
			total += len(list(filter(propiedadBuscada, self._juego.mano)))
		if zonaABuscar in [JugadorBase.Zona.MI_ZONA_DÚOS, JugadorBase.Zona.TODO_MÍO]:
			# Buscamos en la zona de dúos del jugador
			total += len(list(filter(propiedadBuscada, map(lambda d: d[0], self._juego.zonaDeDúos.elements()))))
			total += len(list(filter(propiedadBuscada, map(lambda d: d[1], self._juego.zonaDeDúos.elements()))))
		if zonaABuscar == JugadorBase.Zona.TODO_EL_JUEGO:
			total += len(list(filter(propiedadBuscada, cartasDelJuego())))
		
		return total
	
	def _cantidadDeCartasDeTipoEn(self, tipoBuscado: Carta.Tipo, zonaABuscar: Zona):
		"""
		Devuelve la cantidad de cartas de un tipo en la Zona indicada (ver `JugadorBase.Zona`)
		"""
		return self._cantidadDeCartasQueCumplenEn(lambda c: c.tipo == tipoBuscado, zonaABuscar)
	
	def _cantidadDeCartasDeColorEn(self, colorBuscado: Carta.Color, zonaABuscar: Zona):
		"""
		Devuelve la cantidad de cartas de un color en la Zona indicada (ver `JugadorBase.Zona`)
		"""
		return self._cantidadDeCartasQueCumplenEn(lambda c: c.color == colorBuscado, zonaABuscar)
	
	def _cantidadDeDúosDeTipoJugadosPorJugador(self, tipoBuscado: Carta.Tipo, jugadorARevisar: int) -> int:
		"""
		Devuelve la cantidad de dúos jugados por el jugador con número indicado. Funciona para dúos de nadador y tiburón pasándole `tipoBuscado` = `Carta.Tipo.NADADOR` o `CARTA.Tipo.TIBURÓN`, es lo mismo.
		"""
		return len(list(filter(lambda d: d[0].tipo == tipoBuscado or d[1].tipo == tipoBuscado, self._juego.zonaDeDúosDelJugador(jugadorARevisar).elements())))
	# --------------------------------------------------------------------------
	# ---------------------------- Reglas del juego ----------------------------
	def _valorDePrimerColeccionableDeTipo(self, tipo: Carta.Tipo) -> int:
		"""
		Devuelve cuántos puntos otorga conseguir el primer coleccionable del tipo dado.
		"""
		if tipo == Carta.Tipo.ANCLA:
			return 0
		elif tipo == Carta.Tipo.CONCHA:
			return 0
		elif tipo == Carta.Tipo.PULPO:
			return 0
		elif tipo == Carta.Tipo.PINGUINO:
			return 1
		else:
			raise Exception("El tipo enviado no es de coleccionable!")
	
	def _valorDeMúltiplesColeccionablesDeTipo(self, tipo: Carta.Tipo) -> int:
		"""
		Devuelve cuántos puntos otorga conseguir coleccionables subsiguientes del tipo dado.
		"""
		if tipo == Carta.Tipo.ANCLA:
			return 5
		elif tipo == Carta.Tipo.CONCHA:
			return 2
		elif tipo == Carta.Tipo.PULPO:
			return 3
		elif tipo == Carta.Tipo.PINGUINO:
			return 2
		else:
			raise Exception("El tipo enviado no es de coleccionable!")
	
	def _bonificaciónPorMultiplicadorDeTipo(self, tipo: Carta.Tipo) -> int:
		"""
		Devuelve cuántos puntos otorga el multiplicador del tipo dado por cada carta del tipo que afecta.
		"""
		if tipo == Carta.Tipo.CAPITÁN:
			return 3
		elif tipo == Carta.Tipo.COLONIA:
			return 2
		elif tipo == Carta.Tipo.FARO:
			return 1
		elif tipo == Carta.Tipo.CARDUMEN:
			return 1
		else:
			raise Exception("El tipo enviado no es de multiplicador!")
	
	def _tipoBonificadoPorMultiplicadorDeTipo(self, tipo: Carta.Tipo) -> Carta.Tipo:
		"""
		Devuelve cuál tipo es afectado por el multiplicador del tipo dado.
		"""
		if tipo == Carta.Tipo.CAPITÁN:
			return Carta.Tipo.ANCLA
		elif tipo == Carta.Tipo.COLONIA:
			return Carta.Tipo.PINGUINO
		elif tipo == Carta.Tipo.FARO:
			return Carta.Tipo.BARCO
		elif tipo == Carta.Tipo.CARDUMEN:
			return Carta.Tipo.PEZ
		else:
			raise Exception("El tipo enviado no es de multiplicador!")
	# --------------------------------------------------------------------------
	# ---------------------------- Colores y Sirenas ---------------------------
	def _cantidadDeCartasDeColorDescendientes(self, agregarSirena: bool = False) -> list[int]:
		"""
		Devuelve una lista con la cantidad de cartas de cada color en pertenencia, ordenado decrecientemente por cantidad.
		Si `agregarSirena` está seteado, a las cartas en pertenencia se le agrega una sirena adicional
		(útil para considerar cúantos puntos daría agarrar una sirena).
		
		Ejemplo: para un jugador con dos cartas azules, una carta verde, y una carta blanca, devuelve el arreglo `[2,1,1]`
		"""
		cantidadDeCartasDeColor = {color: 0 for color in Carta.Color}
		
		if agregarSirena:
			cantidadDeCartasDeColor[Carta.Color.BLANCO] += 1
		
		for claveDeCarta in self._juego.mano:
			cantidadDeCartasDeColor[claveDeCarta.color] += self._juego.mano[claveDeCarta]
		for claveDeDúo in self._juego.zonaDeDúos:
			cantidadDeCartasDeColor[claveDeDúo[0].color] += self._juego.zonaDeDúos[claveDeDúo]
			cantidadDeCartasDeColor[claveDeDúo[1].color] += self._juego.zonaDeDúos[claveDeDúo]
		
		return (sorted(list(cantidadDeCartasDeColor.values()), reverse=True))
	
	def _coloresDescendientesPorCantidad(self) -> list[Carta.Color]:
		"""
		Devuelve una lista con los colores que el jugador tiene, ordenado decrecientemente por cantidad de cartas del color.
		(útil para calcular qué color toma cada sirena).
		
		Ejemplo: para un jugador con cuatro cartas azules, dos cartas verdes, y una carta blanca, devuelve el arreglo `[Carta.Color.AZUL, Carta.Color.VERDE, Carta.Color.BLANCO]` 
		"""
		cantidadDeCartasDeColor = {}
		
		for claveDeCarta in self._juego.mano:
			if cantidadDeCartasDeColor.get(claveDeCarta.color) == None:
				cantidadDeCartasDeColor[claveDeCarta.color] = 0
			cantidadDeCartasDeColor[claveDeCarta.color] += self._juego.mano[claveDeCarta]
		for claveDeDúo in self._juego.zonaDeDúos:
			if cantidadDeCartasDeColor.get(claveDeDúo[0].color) == None:
				cantidadDeCartasDeColor[claveDeDúo[0].color] = 0
			cantidadDeCartasDeColor[claveDeDúo[0].color] += self._juego.zonaDeDúos[claveDeDúo]
			if cantidadDeCartasDeColor.get(claveDeDúo[1].color) == None:
				cantidadDeCartasDeColor[claveDeDúo[1].color] = 0
			cantidadDeCartasDeColor[claveDeDúo[1].color] += self._juego.zonaDeDúos[claveDeDúo]
		
		return list(sorted(cantidadDeCartasDeColor, key=cantidadDeCartasDeColor.get, reverse=True))
	# --------------------------------------------------------------------------
	# ------------------------ Encontrar Dúos y Acciones -----------------------
	def _buscarDúoParaJugar(self, tipo: Carta.Tipo) -> Multiset[Carta]|None:
		cartasDelDúoEnMano = Multiset([])
		nadadorEncontrado = False
		tiburónEncontrado = False
		for cartaEnMano in self._juego.mano.elements():
			if tipo in [Carta.Tipo.NADADOR, Carta.Tipo.TIBURÓN]:
				if (cartaEnMano.tipo == Carta.Tipo.NADADOR and not nadadorEncontrado) or (cartaEnMano.tipo == Carta.Tipo.TIBURÓN and not tiburónEncontrado):
					cartasDelDúoEnMano[cartaEnMano] += 1
					if cartaEnMano.tipo == Carta.Tipo.NADADOR:
						nadadorEncontrado = True
					else:
						tiburónEncontrado = True
			else: 
				if cartaEnMano.tipo == tipo:
					cartasDelDúoEnMano[cartaEnMano] += 1
			if cartasDelDúoEnMano.total() == 2:
				return cartasDelDúoEnMano
		return None
	# --------------------------------------------------------------------------
