from collections import Counter as Multiset
from administrador.acción import Acción
from juego.carta import Carta
from juego.partida import PartidaDeOcéanos
from administrador.evento import Evento
from ..base import JugadorBase
from jugador.registro import registrarComo

@registrarComo("decisiones_cacheadas")
class JugadorDecisionesCacheadas(JugadorBase):
	# ========================= INTERFAZ DE JUEGO =========================
	def __init__(self) -> None:
		super().__init__()
		self.olvidarTodo()
	
	def configurarParaJuego(self, juego: PartidaDeOcéanos, númeroDeJugador: int, listaDeEventos: list[Evento]) -> None:
		super().configurarParaJuego(juego, númeroDeJugador, listaDeEventos)
	
	def decidirAcciónDeRobo(self) -> Acción.Robo:
		if self.acciónDeRobo == "no_sé":
			raise Exception("¡Este bot no sabe qué elegir!")
		
		acciónDeRobo = self.acciónDeRobo
		self.acciónDeRobo = "no_sé"
		
		return acciónDeRobo
	
	def decidirCómoRobarDelMazo(self, opcionesDeRobo: list[Carta]) -> tuple[int, int|None]:
		if self.cartaARobarDelMazo == "no_sé" or self.pilaDeDescarteDondeDescartarOtroRobo == "no_sé":
			raise Exception("¡Este bot no sabe qué elegir!")
		
		cartaARobarDelMazo = self.cartaARobarDelMazo
		pilaDeDescarteDondeDescartarOtroRobo = self.pilaDeDescarteDondeDescartarOtroRobo
		self.cartaARobarDelMazo = "no_sé"
		self.pilaDeDescarteDondeDescartarOtroRobo = "no_sé"
		
		return [cartaARobarDelMazo, pilaDeDescarteDondeDescartarOtroRobo]
	
	def decidirAcciónDeDúos(self) -> tuple[Acción.Dúos, Multiset[Carta]|None, tuple[any]|None]:
		if self.acciónDeDúos == "no_sé" or self.cartasDeDúoAJugar == "no_sé" or self.parámetrosDeDúo == "no_sé":
			raise Exception("¡Este bot no sabe qué elegir!")
		
		acciónDeDúos = self.acciónDeDúos
		cartasDeDúoAJugar = self.cartasDeDúoAJugar
		parámetrosDeDúo = self.parámetrosDeDúo
		self.acciónDeDúos = "no_sé"
		self.cartasDeDúoAJugar = "no_sé"
		self.parámetrosDeDúo = "no_sé"
		
		return [acciónDeDúos, cartasDeDúoAJugar, parámetrosDeDúo]
	
	def decidirQuéRobarConDúoDeCangrejos(self, descarteElegido: list[Carta]) -> int:
		if self.cartaElegidaParaRobarConDúoDeCangrejo == "no_sé":
			raise Exception("¡Este bot no sabe qué elegir!")
		
		cartaElegidaParaRobarConDúoDeCangrejo = self.cartaElegidaParaRobarConDúoDeCangrejo
		self.cartaElegidaParaRobarConDúoDeCangrejo = "no_sé"
		
		return cartaElegidaParaRobarConDúoDeCangrejo
	
	def decidirAcciónDeFinDeTurno(self) -> Acción.FinDeTurno:
		if self.acciónDeFinDeTurno == "no_sé":
			raise Exception("¡Este bot no sabe qué elegir!")
		
		acciónDeFinDeTurno = self.acciónDeFinDeTurno
		self.acciónDeFinDeTurno = "no_sé"
		
		return acciónDeFinDeTurno
	
	def configurarInicioDeRonda(self, cartasInicialesDelDescarte: tuple[Carta, Carta]) -> None:
		pass
	
	def configurarFinDeRonda(self, manos: list[Multiset[Carta]], puntajesDeRonda: list[int]) -> None:
		self.olvidarTodo()
	
	def configurarInicioDeTurno(self) -> None:
		pass
	
	# ============================ AUXILIARES =============================	
	def olvidarTodo(self) -> None:
		self.acciónDeRobo = "no_sé"
		self.acciónDeDúos = "no_sé"
		self.acciónDeFinDeTurno = "no_sé"
		self.cartaARobarDelMazo = "no_sé"
		self.pilaDeDescarteDondeDescartarOtroRobo = "no_sé"
		self.cartasDeDúoAJugar = "no_sé"
		self.parámetrosDeDúo = "no_sé"
		self.cartaElegidaParaRobarConDúoDeCangrejo = "no_sé"
	