from collections import Counter as Multiset
from administrador.acción import Acción
from administrador.evento import Evento
from copy import deepcopy
from random import choice
from juego.carta import Carta
from juego.partida import PartidaDeOcéanos, SIRENAS_INF, cartasDelJuego
from ..base import JugadorBase

class PuntosBotMk2(JugadorBase):
	# ========================= INTERFAZ DE JUEGO =========================
	def __init__(self):
		super().__init__()
		
		self._juguéPeces: bool = False
		self._copiaDeMiMano: Multiset[Carta] = None
		self._primerEventoNoLeído: int = 0
		self._pilaARobarConCangrejos: int = None
		
		self._mazoEstimado: Multiset[Carta] = Multiset(cartasDelJuego())
		self._descarteEstimado: tuple[Multiset[Carta], Multiset[Carta]] = (Multiset([]), Multiset([]))
		self._manosEstimadas: list[Multiset[Carta]] = None
		
		
		with open("configuracion_mk2.txt", "r") as configfile:
			self.COEF_MULTIPLICADOR_OBTENIDO = float(configfile.readline().split("=")[1].strip())
			self.PLUS_OBTENER_MULTIPLICADOR = float(configfile.readline().split("=")[1].strip())
			arrancarColeccionable = float(configfile.readline().split("=")[1].strip())
			self.COEF_ARRANCAR_COLECCIONABLE = dict((col, arrancarColeccionable) for col in [Carta.Tipo.CONCHA, Carta.Tipo.PULPO, Carta.Tipo.ANCLA, Carta.Tipo.PINGUINO])
			#*self.VALOR_BASE_PRIMER_CARTA_DUO = float(configfile.readline().split("=")[1].strip())
			self.COEF_COMPLETAR_DUO = float(configfile.readline().split("=")[1].strip())
			self.PLUS_SIRENA = float(configfile.readline().split("=")[1].strip())
			# ==============================
			self.COEF_SEGUIR_COLECCIONABLE = float(configfile.readline().split("=")[1].strip())
			primerPez = float(configfile.readline().split("=")[1].strip())
			primerBarco = float(configfile.readline().split("=")[1].strip())
			primerCangrejo = float(configfile.readline().split("=")[1].strip())
			primerNadadorTiburón = float(configfile.readline().split("=")[1].strip())
			self.PLUS_PRIMER_DÚO = {
				Carta.Tipo.PEZ: primerPez,
				Carta.Tipo.BARCO: primerBarco,
				Carta.Tipo.CANGREJO: primerCangrejo,
				Carta.Tipo.NADADOR: primerNadadorTiburón,
				Carta.Tipo.TIBURÓN: primerNadadorTiburón
			}
		
		#*self.COEF_MULTIPLICADOR_OBTENIDO = 1.0
		self.VALOR_PROXIMO_COLECCIONABLE = {
			Carta.Tipo.CONCHA: 2.0 * self.COEF_SEGUIR_COLECCIONABLE,
			Carta.Tipo.PULPO: 3.0 * self.COEF_SEGUIR_COLECCIONABLE,
			Carta.Tipo.PINGUINO: 2.0 * self.COEF_SEGUIR_COLECCIONABLE,
			Carta.Tipo.ANCLA: 5.0 * self.COEF_SEGUIR_COLECCIONABLE
		}
		self.VALOR_PRIMER_COLECCIONABLE = {
			Carta.Tipo.CONCHA: 0.0,
			Carta.Tipo.PULPO: 0.0,
			Carta.Tipo.PINGUINO: 1.0,
			Carta.Tipo.ANCLA: 0.0
		}
		
		#*self.COEF_ARRANCAR_COLECCIONABLE = {
		#*	Carta.Tipo.CONCHA: 2.0,
		#*	Carta.Tipo.PULPO: 2.0,
		#*	Carta.Tipo.PINGUINO: 2.0,
		#*	Carta.Tipo.ANCLA: 2.0
		#*}
		#*self.PLUS_OBTENER_MULTIPLICADOR = 0.0
		#*self.VALOR_BASE_PRIMER_CARTA_DUO = 1.0
		#*self.COEF_COMPLETAR_DUO = 3.0
		#*self.PLUS_SIRENA = 10.0
		
		
		
		
	
	def decidirAcciónDeRobo(self):
		# Comparamos el valor estimado de nuestras opciones
		valorEstimadoMazo = self._valorPromedioMazoEstimado()
		valorEstimadoDescarte0 = (
			self._valorDeCarta(self._juego.topeDelDescarte[0], explorar=True)
			if self._juego.cantidadDeCartasEnDescarte[0] > 0 else -1.0
		)
		valorEstimadoDescarte1 = (
			self._valorDeCarta(self._juego.topeDelDescarte[1], explorar=True)
			if self._juego.cantidadDeCartasEnDescarte[1] > 0 else -1.0
		)
		
		##print(f"Valor mazo: {valorEstimadoMazo:.2f}")
		##print(f"Valor descarte 0: {valorEstimadoDescarte0:.2f}")
		##print(f"Valor descarte 1: {valorEstimadoDescarte1:.2f}")
		
		mejorOpción = max(valorEstimadoMazo, valorEstimadoDescarte0, valorEstimadoDescarte1)
		if valorEstimadoMazo == mejorOpción:
			return Acción.Robo.DEL_MAZO
		elif valorEstimadoDescarte0 == mejorOpción:
			# Hemos robado una carta del descarte; podemos
			#   eliminar la carta del descarte.
			self._descarteEstimado[0][self._juego.topeDelDescarte[0]] -= 1
			if self._descarteEstimado[0][self._juego.topeDelDescarte[0]] == 0:
				del self._descarteEstimado[0][self._juego.topeDelDescarte[0]]
			return Acción.Robo.DEL_DESCARTE_0
		else:
			# Hemos robado una carta del descarte; podemos
			#   eliminar la carta del descarte.
			self._descarteEstimado[1][self._juego.topeDelDescarte[1]] -= 1
			if self._descarteEstimado[1][self._juego.topeDelDescarte[1]] == 0:
				del self._descarteEstimado[1][self._juego.topeDelDescarte[1]]
			return Acción.Robo.DEL_DESCARTE_1
	
	def decidirCómoRobarDelMazo(self, opcionesDeRobo):
		for cartaDelMazo in opcionesDeRobo:
			# Hemos visto esta carta salir del mazo; podemos
			#   sacarla del mazo estimado
			self._mazoEstimado[cartaDelMazo] -= 1
			if self._mazoEstimado[cartaDelMazo] == 0:
				del self._mazoEstimado[cartaDelMazo]
		
		if len(opcionesDeRobo) == 1:
			return (0, None)
		
		pilaDondeDescartar = None
		
		# Comparamos el valor estimado de ambas cartas
		valorPrimeraCarta = self._valorDeCarta(opcionesDeRobo[0], explorar=True)
		valorSegundaCarta = self._valorDeCarta(opcionesDeRobo[1], explorar=True)
		
		##print(f"Valor carta 0: {valorPrimeraCarta:.2f} ({opcionesDeRobo[0]})")
		##print(f"Valor carta 1: {valorSegundaCarta:.2f} ({opcionesDeRobo[1]})")
		
		
		mejorOpción = max(valorPrimeraCarta, valorSegundaCarta)
		
		cartaARobar = 0 if valorPrimeraCarta == mejorOpción else 1
		
		# Por ahora elegimos random en qué pila descartar
		if self._juego.cantidadDeCartasEnDescarte[0] > 0 and self._juego.cantidadDeCartasEnDescarte[1] == 0:
			pilaDondeDescartar = 1
		elif self._juego.cantidadDeCartasEnDescarte[1] > 0 and self._juego.cantidadDeCartasEnDescarte[0] == 0:
			pilaDondeDescartar = 0
		else:
			pilaDondeDescartar = choice([0,1])
		
		# Hemos descartado la carta no elegida en la pila elegida; podemos
		#   agregar la carta descartada al descarte correspondiente
		self._descarteEstimado[pilaDondeDescartar][opcionesDeRobo[1 - cartaARobar]] += 1
		
		return (cartaARobar, pilaDondeDescartar)
	
	def decidirAcciónDeDúos(self):
		# Pequeño checkeo para considerar la carta que recién robé con dúo de peces
		if self._juguéPeces:
			if not (
				self._listaDeEventos[-1].jugador == self._númeroDeJugador and
				self._listaDeEventos[-1].acción == Acción.Dúos.JUGAR_PECES
			):
				raise Exception("Le erré con los eventos!")
			manoActual = deepcopy(self._juego.mano)
			manoActual.subtract(self._copiaDeMiMano)
			
			cartaRobadaConPeces = None
			
			for carta in manoActual.elements():
				if manoActual[carta] > 0:
					cartaRobadaConPeces = carta
					break
			
			
			cartaRobadaConPeces = list(manoActual.elements())[0]
			
			
			
			# Hemos robado una carta del mazo; podemos sacarla del mazo estimado
			self._mazoEstimado[cartaRobadaConPeces] -= 1
			if self._mazoEstimado[cartaRobadaConPeces] == 0:
				del self._mazoEstimado[cartaRobadaConPeces]
			
			self._juguéPeces = False
		
		
		if self._buscarDúoParaJugar(Carta.Tipo.BARCO) != None:
			# Si se puede, jugar un dúo de barcos
			return (Acción.Dúos.JUGAR_BARCOS, self._buscarDúoParaJugar(Carta.Tipo.BARCO), None)
		elif (
			self._buscarDúoParaJugar(Carta.Tipo.CANGREJO) != None and
			(
				self._juego.cantidadDeCartasEnDescarte[0] != 0 or
				self._juego.cantidadDeCartasEnDescarte[1] != 0
			) and
			(
				len(self._descarteEstimado[0]) > 0 or
				len(self._descarteEstimado[1]) > 0
			)
		):
			# Si se puede, jugar un dúo de cangrejos
			mejorCartaDelDescarteEstimado = (None, None) # (pila, índice)
			mejorValorDelDescarteEstimado = -1.0
			
			
			for i, cartaEnDescarteEstimado in enumerate(self._descarteEstimado[0]):
				valorDeCarta = self._valorDeCarta(cartaEnDescarteEstimado, explorar=True)
				if valorDeCarta > mejorValorDelDescarteEstimado:
					mejorCartaDelDescarteEstimado = (0, i)
					mejorValorDelDescarteEstimado = valorDeCarta
			for i, cartaEnDescarte in enumerate(self._descarteEstimado[1]):
				valorDeCarta = self._valorDeCarta(cartaEnDescarte, explorar=True)
				if valorDeCarta > mejorValorDelDescarteEstimado:
					mejorCartaDelDescarteEstimado = (1, i)
					mejorValorDelDescarteEstimado = valorDeCarta
			
			
			
			
			pilaARobar = mejorCartaDelDescarteEstimado[0]
			cartaARobar = self._descarteEstimado[pilaARobar][mejorCartaDelDescarteEstimado[1]]
			
			
			##print(f"CREO QUE Mejor valor para robar con cangrejos: {mejorValorDelDescarteEstimado} ({cartaARobar})")
			
			self._pilaARobarConCangrejos = pilaARobar
			
			
			#! QUICKFIX: no intentes robar de una pila vacía...
			if self._juego.cantidadDeCartasEnDescarte[pilaARobar] == 0:
				return (Acción.Dúos.NO_JUGAR, None, None)
			
			
			return (Acción.Dúos.JUGAR_CANGREJOS, self._buscarDúoParaJugar(Carta.Tipo.CANGREJO), (pilaARobar,))
		
		elif (
			self._buscarDúoParaJugar(Carta.Tipo.PEZ) != None and
			self._juego.cantidadDeCartasEnMazo > 0
		):
			# Si se puede, jugar un dúo de peces
			# Tengo que hacer esto para poder sacar la carta robada del mazo 
			self._juguéPeces = True
			self._copiaDeMiMano = deepcopy(self._juego.mano)
			dúoAJugar = self._buscarDúoParaJugar(Carta.Tipo.PEZ)
			self._copiaDeMiMano[list(dúoAJugar.elements())[0]] -= 1
			if self._copiaDeMiMano[list(dúoAJugar.elements())[0]] == 0:
				del self._copiaDeMiMano[list(dúoAJugar.elements())[0]]
			self._copiaDeMiMano[list(dúoAJugar.elements())[1]] -= 1
			if self._copiaDeMiMano[list(dúoAJugar.elements())[1]] == 0:
				del self._copiaDeMiMano[list(dúoAJugar.elements())[1]]
			return (Acción.Dúos.JUGAR_PECES, dúoAJugar, None)
		
		elif self._buscarDúoParaJugar(Carta.Tipo.NADADOR) != None and not self._juego.últimaChanceEnCurso():
			# Si se puede, jugar dúo de nadador y tiburón
			mejorManoEstimada = self._mejorManoEstimadaAdversarios()
			
			##print(f"Mejor valor de jugador a robar: {mejorManoEstimada[1]:.2f} (jugador {mejorManoEstimada[0]})")
			
			#! QUICKFIX: no intentes robar a una mano vacía...
			if mejorManoEstimada == None:
				return (Acción.Dúos.NO_JUGAR, None, None)
			
			return (
				Acción.Dúos.JUGAR_NADADOR_Y_TIBURÓN,
				self._buscarDúoParaJugar(Carta.Tipo.NADADOR),
				(mejorManoEstimada[0],)
			)
		else:
			# Si no se puede jugar ningún dúo, entonces no jugar nada
			return (Acción.Dúos.NO_JUGAR, None, None)
	
	def decidirQuéRobarConDúoDeCangrejos(self, descarteElegido: list[Carta]) -> int:
		mejorCartaDelDescarte = None # (pila, índice)
		mejorValorDelDescarte = -1.0
		
		for i, cartaEnDescarteElegido in enumerate(descarteElegido):
			valorDeCarta = self._valorDeCarta(cartaEnDescarteElegido, explorar=True)
			if valorDeCarta > mejorValorDelDescarte:
				mejorCartaDelDescarte = i
				mejorValorDelDescarte = valorDeCarta
		
		
		cartaARobar = descarteElegido[mejorCartaDelDescarte]
		
		##print(f"Mejor valor para robar con cangrejos: {mejorValorDelDescarte} ({cartaARobar})")
		
		
		# Hemos visto la totalidad de la pila de descarte elegida; podemos actualizar nuestra información
		self._descarteEstimado[self._pilaARobarConCangrejos].clear()
		for carta in descarteElegido:
			self._descarteEstimado[self._pilaARobarConCangrejos][carta] += 1
		
		# Y ahora vamos a sacar una carta del descarte; podemos sacarla del descarte estimado
		self._descarteEstimado[self._pilaARobarConCangrejos][cartaARobar] -= 1
		if self._descarteEstimado[self._pilaARobarConCangrejos][cartaARobar] == 0:
			del self._descarteEstimado[self._pilaARobarConCangrejos][cartaARobar]
		
		self._pilaARobarConCangrejos = None
		return mejorCartaDelDescarte
	
	def decidirAcciónDeFinDeTurno(self):
		if self._juego.puntajeDeRonda >= 7 and not self._juego.últimaChanceEnCurso():
			# Si puedo terminar la ronda, hagamos 50/50 de cómo hacerlo
			return choice([Acción.FinDeTurno.DECIR_BASTA, Acción.FinDeTurno.DECIR_ÚLTIMA_CHANCE])
		else:
			# Si sólo se puede pasar de turno, hacerlo
			return Acción.FinDeTurno.PASAR_TURNO
	
	def configurarParaJuego(self, juego, númeroDeJugador, listaDeEventos):
		super().configurarParaJuego(juego, númeroDeJugador, listaDeEventos)
		self._manosEstimadas = [ Multiset([]) for _ in range(self._juego.cantidadDeJugadores) ]
	
	def configurarInicioDeRonda(self, cartasInicialesDelDescarte):
		# Considero las cartas en el tope del descarte para mi estimación.
		#    Es decir, sacamos las cartas del mazo y las agregamos al descarte
		self._descarteEstimado[0][cartasInicialesDelDescarte[0]] += 1
		self._mazoEstimado[cartasInicialesDelDescarte[0]] -= 1
		if self._mazoEstimado[cartasInicialesDelDescarte[0]] == 0:
			del self._mazoEstimado[cartasInicialesDelDescarte[0]]
		self._descarteEstimado[1][cartasInicialesDelDescarte[1]] += 1
		self._mazoEstimado[cartasInicialesDelDescarte[1]] -= 1
		if self._mazoEstimado[cartasInicialesDelDescarte[1]] == 0:
			del self._mazoEstimado[cartasInicialesDelDescarte[1]]
	
	def configurarFinDeRonda(self, manos, puntajesDeRonda):
		self._primerEventoNoLeído = 0
		self._mazoEstimado = Multiset(cartasDelJuego())
		self._descarteEstimado = (Multiset([]), Multiset([]))
		self._manosEstimadas = [ Multiset([]) for _ in range(self._juego.cantidadDeJugadores) ]
	
	def configurarInicioDeTurno(self):
		evento: Evento = None
		while self._primerEventoNoLeído < len(self._listaDeEventos):
			evento = self._listaDeEventos[self._primerEventoNoLeído]
			if evento.jugador == self._númeroDeJugador:
				# No analizar eventos propios
				self._primerEventoNoLeído += 1
				continue
			
			if evento.acción in [Acción.Robo.DEL_DESCARTE_0, Acción.Robo.DEL_DESCARTE_1]:
				# Otro jugador robó una carta del descarte; podemos agregar
				#   la carta a la mano del adversario, y eliminar la carta
				#   del descarte.
				pila = 0 if evento.acción == Acción.Robo.DEL_DESCARTE_0 else 1
				self._manosEstimadas[evento.jugador][evento.parámetros["cartaRobada"]] += 1
				self._descarteEstimado[pila][evento.parámetros["cartaRobada"]] -= 1
				if self._descarteEstimado[pila][evento.parámetros["cartaRobada"]] == 0:
					del self._descarteEstimado[pila][evento.parámetros["cartaRobada"]]
			
			elif evento.acción == Acción.Robo.DEL_MAZO and evento.parámetros["cartaDescartada"] != None:
				# Otro jugador robó una carta del mazo y descartó la otra; podemos
				#   agregar la carta descartada al descarte y eliminarla del mazo
				self._descarteEstimado[evento.parámetros["pilaDondeDescartó"]][evento.parámetros["cartaDescartada"]] += 1
				self._mazoEstimado[evento.parámetros["cartaDescartada"]] -= 1
				if self._mazoEstimado[evento.parámetros["cartaDescartada"]] == 0:
					del self._mazoEstimado[evento.parámetros["cartaDescartada"]]
			
			elif evento.acción in Acción.Dúos:
				# Otro jugador jugó algún tipo de dúo; podemos eliminar las cartas
				#   jugadas del mazo, y si habíamos estimado que estaban en su mano,
				#   podemos sacarlas de la estimación
				
				self._mazoEstimado[evento.parámetros["cartasJugadas"][0]] -= 1
				if self._mazoEstimado[evento.parámetros["cartasJugadas"][0]] == 0:
					del self._mazoEstimado[evento.parámetros["cartasJugadas"][0]]
				self._mazoEstimado[evento.parámetros["cartasJugadas"][1]] -= 1
				if self._mazoEstimado[evento.parámetros["cartasJugadas"][1]] == 0:
					del self._mazoEstimado[evento.parámetros["cartasJugadas"][1]]
				
				if self._manosEstimadas[evento.jugador][evento.parámetros["cartasJugadas"][0]] > 0:
					self._manosEstimadas[evento.jugador][evento.parámetros["cartasJugadas"][0]] -= 1
					if self._manosEstimadas[evento.jugador][evento.parámetros["cartasJugadas"][0]] == 0:
						del self._manosEstimadas[evento.jugador][evento.parámetros["cartasJugadas"][0]]
				if self._manosEstimadas[evento.jugador][evento.parámetros["cartasJugadas"][1]] > 0:
					self._manosEstimadas[evento.jugador][evento.parámetros["cartasJugadas"][1]] -= 1
					if self._manosEstimadas[evento.jugador][evento.parámetros["cartasJugadas"][1]] == 0:
						del self._manosEstimadas[evento.jugador][evento.parámetros["cartasJugadas"][1]]
				
				
				# Además, si fue un Nadador y Tiburón y nos robó a nosotros, sabemos
				#   que la carta que nos robó ahora está en su mano
				if (
					evento.acción == Acción.Dúos.JUGAR_NADADOR_Y_TIBURÓN and
					evento.parámetros["jugadorRobado"] == self._númeroDeJugador and
					evento.parámetros["cartaRobada"] != None
				):
					self._manosEstimadas[evento.jugador][evento.parámetros["cartaRobada"]] += 1
			
			self._primerEventoNoLeído += 1
		
		##self._printValorDeTodasLasCartas()
	
	# ============================ AUXILIARES =============================
	def _valorDeCarta(self, carta: Carta, explorar: bool = False) -> float:
		valor = 0.0
		# Primero, aumentamos el valor en caso de que tengamos el multiplicador correspondiente en mano
		if carta.tipo == Carta.Tipo.BARCO and self._cantidadDeCartasDeTipoEnMano(Carta.Tipo.FARO) > 0:
			valor += 1.0 * self.COEF_MULTIPLICADOR_OBTENIDO
		elif carta.tipo == Carta.Tipo.ANCLA and self._cantidadDeCartasDeTipoEnMano(Carta.Tipo.CAPITÁN) > 0:
			valor += 3.0 * self.COEF_MULTIPLICADOR_OBTENIDO
		elif carta.tipo == Carta.Tipo.PINGUINO and self._cantidadDeCartasDeTipoEnMano(Carta.Tipo.COLONIA) > 0:
			valor += 2.0 * self.COEF_MULTIPLICADOR_OBTENIDO
		elif carta.tipo == Carta.Tipo.PEZ and self._cantidadDeCartasDeTipoEnMano(Carta.Tipo.CARDUMEN) > 0:
			valor += 1.0 * self.COEF_MULTIPLICADOR_OBTENIDO
		
		
		if carta.esColeccionable():
			if self._cantidadDeCartasDeTipoEnMano(carta.tipo) > 0:
				# Si ya tenemos una carta del tipo de coleccionable, su valor es cuánto suma conseguir otro
				valor += self.VALOR_PROXIMO_COLECCIONABLE[carta.tipo]
			else:
				# Si no tenemos una carta del tipo de coleccionable, su valor es cuánto suma conseguir el primero
				#   y un poco de bonificación por qué tan probable es conseguir otro coleccionable del tipo 
				valor += (
					self.VALOR_PRIMER_COLECCIONABLE[carta.tipo] +
					(
						self.COEF_ARRANCAR_COLECCIONABLE[carta.tipo]
						* self._cantidadDeCartasDeTipoEnMazoEstimado(carta.tipo)
						/ self._juego.cantidadDeCartasEnMazo
					)
				)
		elif carta.esMultiplicador():
			# El valor es cuántos puntos ganaríamos ahora mismo de tener el multiplicador
			valor += (
				self._cantidadDeCartasDeTipoEnMano(self._tipoAfectadoPorMultiplicador(carta.tipo)) *
				self._bonificacionPorMultiplicador(carta.tipo)
			) + self.PLUS_OBTENER_MULTIPLICADOR
		elif carta.tipo == Carta.Tipo.PEZ:
			if self._cantidadDeCartasDeTipoEnMano(carta.tipo) == 0:
				# Si no tenemos una carta para completar el dúo, no vale nada
				valor += 0.0 + self.PLUS_PRIMER_DÚO[carta.tipo]
			else:
				# Si podemos completar el dúo con esta carta, vale el punto del dúo
				#  más el valor promedio que obtenemos de la carta robada
				valor += 1.0 * self.COEF_COMPLETAR_DUO
				if explorar:
					valor += self._valorPromedioMazoEstimado()
		elif carta.tipo == Carta.Tipo.BARCO:
			if self._cantidadDeCartasDeTipoEnMano(carta.tipo) == 0:
				# Si no tenemos una carta para completar el dúo, no vale nada
				valor += 0.0 + self.PLUS_PRIMER_DÚO[carta.tipo]
			else:
				# Si podemos completar el dúo con esta carta, vale el punto del dúo
				#  más lo que sea mejor entre robar alguna carta del tope del descarte
				#  o el valor promedio que obtenemos de robar del mazo
				valor += 1.0 * self.COEF_COMPLETAR_DUO
				if explorar:
					valor += max(
						self._valorPromedioMazoEstimado(),
						self._valorDeCarta(self._juego.topeDelDescarte[0]) if self._juego.cantidadDeCartasEnDescarte[0] > 0 else 0.0,
						self._valorDeCarta(self._juego.topeDelDescarte[1]) if self._juego.cantidadDeCartasEnDescarte[1] > 0 else 0.0
					)
		elif carta.tipo == Carta.Tipo.CANGREJO:
			if self._cantidadDeCartasDeTipoEnMano(carta.tipo) == 0:
				# Si no tenemos una carta para completar el dúo, no vale nada
				valor += 0.0 + self.PLUS_PRIMER_DÚO[carta.tipo]
			else:
				# Si podemos completar el dúo con esta carta, vale el punto del dúo
				#  más el valor de la mejor carta que vimos entrar al descarte y estamos seguros
				#  de que no se fue del descarte (por ser robada del descarte)
				valor += 1.0 * self.COEF_COMPLETAR_DUO
				if explorar:
					valor += self._mejorValorDescarteEstimado()
		elif carta.tipo == Carta.Tipo.NADADOR:
			if self._cantidadDeCartasDeTipoEnMano(Carta.Tipo.TIBURÓN) == 0:
				# Si no tenemos una carta para completar el dúo, no vale nada
				valor += 0.0 + self.PLUS_PRIMER_DÚO[carta.tipo]
			else:
				# Si podemos completar el dúo con esta carta, vale el punto del dúo
				#  más el valor de la mejor carta que vimos entrar a la mano de algún jugador
				valor += 1.0 * self.COEF_COMPLETAR_DUO
				if explorar:
					valor += self._mejorManoEstimadaAdversarios()[1]
		elif carta.tipo == Carta.Tipo.TIBURÓN:
			if self._cantidadDeCartasDeTipoEnMano(Carta.Tipo.NADADOR) == 0:
				# Si no tenemos una carta para completar el dúo, no vale nada
				valor += 0.0 + self.PLUS_PRIMER_DÚO[carta.tipo]
			else:
				# Si podemos completar el dúo con esta carta, vale el punto del dúo
				#  más el valor de la mejor carta que vimos entrar a la mano de algún jugador
				valor += 1.0 * self.COEF_COMPLETAR_DUO
				if explorar:
					valor += self._mejorManoEstimadaAdversarios()[1]
		elif carta.tipo == Carta.Tipo.SIRENA:
			cantidadDeSirenas = self._cantidadDeCartasDeTipoEnMano(Carta.Tipo.SIRENA)
			if cantidadDeSirenas == 3:
				# Si podemos conseguir la cuarta sirena, hemos ganado!
				valor += SIRENAS_INF
			else:
				# Si no, el valor es cuántas cartas tenemos de nuestro mejor color sin sirenas
				valor += (self._cantidadDeCartasDeColorDescendientes() + [0,0,0])[cantidadDeSirenas] + self.PLUS_SIRENA
		
		
		return valor
	
	def _cantidadDeCartasDeTipoEnMano(self, tipo: Carta.Tipo) -> int:
		cantidadDeCartasDeTipo = 0
		for cartaEnMano in self._juego.mano.elements():
			if cartaEnMano.tipo == tipo:
				cantidadDeCartasDeTipo += 1
		return cantidadDeCartasDeTipo
	
	def _valorDePrimerColeccionableTipo(self, tipo: Carta.Tipo) -> int:
		return 1 if tipo == Carta.Tipo.PINGUINO else 0
	
	def _valorDeMúltiplesColeccionableTipo(self, tipo: Carta.Tipo) -> int:
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
	
	def _cantidadDeCartasDeTipoEnMazoEstimado(self, tipo: Carta.Tipo) -> int:
		cantidadDeCartasDeTipo = 0
		for cartaEnMazoEstimado in self._mazoEstimado.elements():
			if cartaEnMazoEstimado.tipo == tipo:
				cantidadDeCartasDeTipo += 1
		return cantidadDeCartasDeTipo
	
	def _tipoAfectadoPorMultiplicador(self, tipo: Carta.Tipo) -> Carta.Tipo:
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
	
	def _bonificacionPorMultiplicador(self, tipo: Carta.Tipo) -> int:
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
	
	def _valorPromedioMazoEstimado(self) -> float:
		valorTotalMazoEstimado = 0.0
		for cartaEnMazoEstimado in self._mazoEstimado.elements():
			valorTotalMazoEstimado += self._valorDeCarta(cartaEnMazoEstimado, explorar=False)
		return valorTotalMazoEstimado / self._mazoEstimado.total()
	
	def _mejorValorDescarteEstimado(self) -> float:
		mejorValorDescarteEstimado = 0.0
		
		for cartaEnDescarteEstimado in self._descarteEstimado[0].elements():
			valorDeCartaEnDescarteEstimado = self._valorDeCarta(cartaEnDescarteEstimado)
			if valorDeCartaEnDescarteEstimado > mejorValorDescarteEstimado:
				mejorValorDescarteEstimado = valorDeCartaEnDescarteEstimado
		
		for cartaEnDescarteEstimado in self._descarteEstimado[1].elements():
			valorDeCartaEnDescarteEstimado = self._valorDeCarta(cartaEnDescarteEstimado)
			if valorDeCartaEnDescarteEstimado > mejorValorDescarteEstimado:
				mejorValorDescarteEstimado = valorDeCartaEnDescarteEstimado
		
		return mejorValorDescarteEstimado
	
	def _mejorManoEstimadaAdversarios(self) -> tuple[int, float]:
		mejorPromedioManoEstimadaAdversarios = -1.0
		mejorAdversario = None
		
		for j in range(self._juego.cantidadDeJugadores):
			if j != self._númeroDeJugador and self._juego.cantidadDeCartasEnManoDelJugador(j) > 0:
				valorTotalManoEstimada = 0.0
				# Calculo el valor de las cartas que sí conozco
				for cartaEnManoEstimada in self._manosEstimadas[j].elements():
					valorTotalManoEstimada += self._valorDeCarta(cartaEnManoEstimada, explorar=False)
				
				# Uso el valor promedio del mazo para cartas en la mano que no conozco
				valorTotalManoEstimada += self._valorPromedioMazoEstimado() * ( self._juego.cantidadDeCartasEnManoDelJugador(j) - self._manosEstimadas[j].total() )
				
				promedioManoEstimada = valorTotalManoEstimada / self._juego.cantidadDeCartasEnManoDelJugador(j)
				
				if promedioManoEstimada > mejorPromedioManoEstimadaAdversarios:
					mejorPromedioManoEstimadaAdversarios = promedioManoEstimada
					mejorAdversario = j
		
		return (mejorAdversario, mejorPromedioManoEstimadaAdversarios)
	
	def _cantidadDeCartasDeColorDescendientes(self) -> list[int]:
		cantidadDeCartasDeColor = {color: 0 for color in Carta.Color}
		
		for claveDeCarta in self._juego.mano:
			cantidadDeCartasDeColor[claveDeCarta.color] += self._juego.mano[claveDeCarta]
		for claveDeDúo in self._juego.zonaDeDúos:
			cantidadDeCartasDeColor[claveDeDúo[0].color] += self._juego.zonaDeDúos[claveDeDúo]
			cantidadDeCartasDeColor[claveDeDúo[1].color] += self._juego.zonaDeDúos[claveDeDúo]
		
		return (sorted(list(cantidadDeCartasDeColor.values()), reverse=True))
	
	def _printValorDeTodasLasCartas(self):
		total = 0.0
		for carta in cartasDelJuego():
			total += self._valorDeCarta(carta, explorar=True)
		for carta in cartasDelJuego():
			valor = self._valorDeCarta(carta, explorar=True)
			print(f"Valor {carta}: {valor * 58.0 / total :.2f}")
		print(f"Valor Total: {total * 58.0 / total :.2f}")