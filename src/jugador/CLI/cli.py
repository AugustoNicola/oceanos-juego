from collections import Counter as Multiset
from administrador.acción import Acción
from administrador.evento import Evento
import cmd
import re
from juego.carta import Carta
from juego.partida import PartidaDeOcéanos
from jugador.base import JugadorBase
from jugador.registro import registrarComo

@registrarComo("jugador_cli")

class JugadorCLI(JugadorBase):
	# ========================= INTERFAZ DE JUEGO =========================
	def __init__(self) -> None:
		super().__init__()
	
	def configurarParaJuego(self, juego: PartidaDeOcéanos, númeroDeJugador: int, listaDeEventos: list[Evento]) -> None:
		super().configurarParaJuego(juego, númeroDeJugador, listaDeEventos)
	
	class Prompt(cmd.Cmd):
		prompt = '>>> '
		
		def __init__(self, jugador):
			super().__init__()
			self.resultado = None
			self.jugador = jugador
		
		def do_juego(self, arg):
			match = re.fullmatch(r'\.(\w+)(\((.*)\))?', arg)
			if not match:
				print("Invocación a \"juego\" inválida")
				return False
			try:
			
				if match.groups()[1] != None:
					# Invocación a método
					método = getattr(self.jugador._juego, match.groups()[0])
					if match.groups()[2] != '':
						print(método(int(match.groups()[2])))
					else:
						print(método())
				else:
					# Invocación a atributo/property
					print(getattr(self.jugador._juego, match.groups()[0]))
			
			except Exception as e:
				print(e)
				print("Ocurrió una excepción al procesar tu comando. Probá nuevamente...")
				return False
		
		def do_chau(self, arg):
			print("chau...")
			return True
		
		def default(self, line):
			print("No entendí. Probá escribir \"?\"")
	
	class AcciónDeRoboPrompt(Prompt):
		prompt = '>>> '
		
		def do_help(self, arg):
			print("\nOpciones de robo posibles:\n- mazo         : ver las cartas del tope del mazo para robar una\n- descarte 0   : robar la carta superior del descarte 0\n- descarte 1   : robar la carta superior del descarte 1\n\nPara ver información del juego, escribir 'juego.<método/atributo de PartidaDeOcéanos>'\nEjemplos:\n- juego.topeDelDescarte\n- juego.últimaChanceEnCurso()\n- juego.mano\n- juego.zonaDeDúosDelJugador(1)")
		
		def do_mazo(self, arg):
			self.resultado = Acción.Robo.DEL_MAZO
			return True
		
		def do_descarte(self, arg):
			if int(arg) == 0:
				self.resultado = Acción.Robo.DEL_DESCARTE_0
				return True
			elif int(arg) == 1:
				self.resultado = Acción.Robo.DEL_DESCARTE_1
				return True
			print(f"'{arg}' no es una pila de descarte válida.")
			return False
	
	class AcciónDeRobarDelMazoPrompt(Prompt):
		prompt = '>>> '
		
		def do_help(self, arg):
			print("\nOpciones:\n- elegir <carta a quedarse> <pila donde descartar>\nEjemplo: elegir 0 1\n\nPara ver información del juego, juego.<método/atributo de PartidaDeOcéanos>\nEjemplos:\n- juego.topeDelDescarte[0]\n- juego.cantidadDeCartasEnMazo\n- juego.mano\n- juego.zonaDeDúos")
		
		def do_elegir(self, arg):
			match = re.fullmatch(r'([01]) ([01])', arg)
			if not match:
				print("Invocación a \"elegir\" inválida")
				return False
			
			self.resultado = (int(match.groups()[0]), int(match.groups()[1]))
			return True
	
	class AcciónDeDúosPrompt(Prompt):
		prompt = '>>> '
		
		def do_help(self, arg):
			print("\nOpciones:\n- no:      no se juegan más dúos este turno\n- peces:   se juega un dúo de peces\n- barcos:  se juega un dúo de barcos\n- cangrejos <índice de pila>:  se juega un dúo de cangrejos para robar de la <índice de pila>-ésima pila\n- nadador <número de jugador>:  se juega un dúo de nadador y tiburón para robarle una carta al jugador <número de jugador>\nEjemplos:\n- no\n- peces\n- barcos\n- cangrejos 0\n- nadador 3\n\nPara ver información del juego, juego.<método/atributo de PartidaDeOcéanos>\nEjemplos:\n- juego.topeDelDescarte[0]\n- juego.cantidadDeCartasEnMazo\n- juego.mano\n- juego.zonaDeDúos")
		
		def do_no(self, arg):
			self.resultado = (Acción.Dúos.NO_JUGAR, None, None)
			return True
		
		def do_peces(self, arg):
			dúoDePeces = self.jugador._buscarDúoParaJugar(Carta.Tipo.PEZ)
			if dúoDePeces == None:
				print("¡No tenés un dúo de peces para jugar!")
				return False
			
			self.resultado = (Acción.Dúos.JUGAR_PECES, dúoDePeces, None)
			return True
		
		def do_barcos(self, arg):
			dúoDeBarcos = self.jugador._buscarDúoParaJugar(Carta.Tipo.BARCO)
			if dúoDeBarcos == None:
				print("¡No tenés un dúo de barcos para jugar!")
				return False
			
			self.resultado = (Acción.Dúos.JUGAR_BARCOS, dúoDeBarcos, None)
			return True
		
		def do_cangrejos(self, arg):
			dúoDeCangrejos = self.jugador._buscarDúoParaJugar(Carta.Tipo.CANGREJO)
			if dúoDeCangrejos == None:
				print("¡No tenés un dúo de cangrejos para jugar!")
				return False
			
			match = re.fullmatch(r'([01])', arg)
			if not match:
				print("Invocación a \"cangrejos\" inválida")
				return False
			
			parámetrosDelDúo = (int(match.groups()[0]),)
			
			self.resultado = (Acción.Dúos.JUGAR_CANGREJOS, dúoDeCangrejos, parámetrosDelDúo)
			return True
		
		def do_nadador(self, arg):
			dúoDeNadadorYTiburón = self.jugador._buscarDúoParaJugar(Carta.Tipo.NADADOR)
			if dúoDeNadadorYTiburón == None:
				print("¡No tenés un dúo de nadador y tiburón para jugar!")
				return False
			
			match = re.fullmatch(r'([0123])', arg)
			if not match:
				print("Invocación a \"nadador\" inválida")
				return False
			
			parámetrosDelDúo = (int(match.groups()[0]),)
			
			self.resultado = (Acción.Dúos.JUGAR_NADADOR_Y_TIBURÓN, dúoDeNadadorYTiburón, parámetrosDelDúo)
			return True
	
	class AcciónDeRobarConCangrejosPrompt(Prompt):
		prompt = '>>> '
		
		def do_help(self, arg):
			print("\nOpciones:\n- elegir <índice de carta>:      se roba la <índice de carta>-ésima carta\nEjemplos:\n- elegir 4\n\nPara ver información del juego, juego.<método/atributo de PartidaDeOcéanos>\nEjemplos:\n- juego.topeDelDescarte[0]\n- juego.cantidadDeCartasEnMazo\n- juego.mano\n- juego.zonaDeDúos")
		
		def do_elegir(self, arg):
			match = re.fullmatch(r'(\d+)', arg)
			if not match:
				print("Invocación a \"elegir\" inválida")
				return False
			
			self.resultado = int(match.groups()[0])
			return True
	
	class AcciónDeFinDeTurnoPrompt(Prompt):
		prompt = '>>> '
		
		def do_help(self, arg):
			print("\nOpciones:\n- pasar:         pasar de turno normalmente\n- basta:         cantar ¡Basta!\n- ultimachance:  cantar ¡Última Chance!\n\nPara ver información del juego, juego.<método/atributo de PartidaDeOcéanos>\nEjemplos:\n- juego.topeDelDescarte[0]\n- juego.cantidadDeCartasEnMazo\n- juego.mano\n- juego.zonaDeDúos")
		
		def do_pasar(self, arg):
			self.resultado = Acción.FinDeTurno.PASAR_TURNO
			return True
		
		def do_basta(self, arg):
			if not self.jugador._juego.puntajeDeRonda >= 7:
				print("No se tienen suficientes puntos para cantar ¡Basta!")
				return False
			self.resultado = Acción.FinDeTurno.DECIR_BASTA
			return True
		
		def do_ultimachance(self, arg):
			if not self.jugador._juego.puntajeDeRonda >= 7:
				print("No se tienen suficientes puntos para cantar ¡Última Chance!")
				return False
			self.resultado = Acción.FinDeTurno.DECIR_ÚLTIMA_CHANCE
			return True
	
	
	
	
	def decidirAcciónDeRobo(self) -> Acción.Robo:
		interfaz = JugadorCLI.AcciónDeRoboPrompt(self)
		interfaz.cmdloop(intro=self._mensajeIntroParaAcciónRoboPrompt())
		print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
		return interfaz.resultado
	
	def decidirCómoRobarDelMazo(self, opcionesDeRobo: list[Carta]) -> tuple[int, int|None]:
		interfaz = JugadorCLI.AcciónDeRobarDelMazoPrompt(self)
		interfaz.cmdloop(intro=self._mensajeIntroParaElegirRoboDelMazoPrompt(opcionesDeRobo))
		print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
		return interfaz.resultado
	
	def decidirAcciónDeDúos(self) -> tuple[Acción.Dúos, Multiset[Carta]|None, tuple[any]|None]:
		interfaz = JugadorCLI.AcciónDeDúosPrompt(self)
		interfaz.cmdloop(intro=self._mensajeIntroParaAcciónDúosPrompt())
		print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
		return interfaz.resultado
	
	def decidirQuéRobarConDúoDeCangrejos(self, descarteElegido: list[Carta]) -> int:
		interfaz = JugadorCLI.AcciónDeRobarConCangrejosPrompt(self)
		interfaz.cmdloop(intro=self._mensajeIntroParaRobarConCangrejosPrompt(descarteElegido))
		print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
		return interfaz.resultado
	
	def decidirAcciónDeFinDeTurno(self) -> Acción.FinDeTurno:
		interfaz = JugadorCLI.AcciónDeFinDeTurnoPrompt(self)
		interfaz.cmdloop(intro=self._mensajeIntroParaAcciónFinDeTurnoPrompt())
		print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
		return interfaz.resultado
	
	def configurarInicioDeRonda(self, cartasInicialesDelDescarte: tuple[Carta, Carta]) -> None:
		pass
	
	def configurarFinDeRonda(self, manos: list[Multiset[Carta]], puntajesDeRonda: list[int]) -> None:
		pass
	
	def configurarInicioDeTurno(self) -> None:
		pass
	
	# ============================ AUXILIARES =============================
	def _mensajeIntroParaAcciónRoboPrompt(self) -> str:
		return f"vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv\nJugador {self._númeroDeJugador}, decidir acción de robo. Para ver cómo, escribir '?'."
	
	def _mensajeIntroParaElegirRoboDelMazoPrompt(self, opcionesDeRobo) -> str:
		return f"vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv\n{opcionesDeRobo}\nJugador {self._númeroDeJugador}, decidir qué carta del mazo quedarse y cuál descartar. Para ver cómo, escribir '?'."
	
	def _mensajeIntroParaAcciónDúosPrompt(self) -> str:
		return f"vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv\nJugador {self._númeroDeJugador}, decidir si se quieren jugar dúos. Para ver cómo, escribir '?'."
	
	def _mensajeIntroParaRobarConCangrejosPrompt(self, descarteElegido) -> str:
		return f"vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv\nLa pila de descarte elegida para robar es:\n{descarteElegido}\nJugador {self._númeroDeJugador}, decidir qué carta del mazo quedarse y cuál descartar. Para ver cómo, escribir '?'."
	
	def _mensajeIntroParaAcciónFinDeTurnoPrompt(self) -> str:
		return f"vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv\nJugador {self._númeroDeJugador}, decidir cómo terminar el turno. Para ver cómo, escribir '?'."
	
	