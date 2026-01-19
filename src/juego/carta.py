from enum import Enum, auto

class CartaInvalidaException(Exception):
	def __init__(self, message="Se intentó crear una carta con atributos inválidos"):
		super().__init__(message)

class Carta():
	class Tipo(Enum):
		CANGREJO = "CANGREJO"
		BARCO = "BARCO"
		PEZ = "PEZ"
		NADADOR = "NADADOR"
		TIBURÓN = "TIBURÓN"
		CONCHA = "CONCHA"
		PULPO = "PULPO"
		PINGUINO = "PINGUINO"
		ANCLA = "ANCLA"
		COLONIA = "COLONIA"
		FARO = "FARO"
		CARDUMEN = "CARDUMEN"
		CAPITÁN = "CAPITÁN"
		SIRENA = "SIRENA"
	
	class Color(Enum):
		AZUL = "AZUL"
		CELESTE = "CELESTE"
		NEGRO = "NEGRO"
		AMARILLO = "AMARILLO"
		VERDE = "VERDE"
		BLANCO = "BLANCO"
		VIOLETA = "VIOLETA"
		GRIS = "GRIS"
		NARANJA_CLARO = "NARANJA_CLARO"
		ROSA = "ROSA"
		NARANJA = "NARANJA"
	
	
	def __init__(self, tipo, color):
		if not isinstance(tipo, Carta.Tipo) or not isinstance(color, Carta.Color):
			raise CartaInvalidaException()
		
		self.tipo = tipo
		self.color = color
		
	def esDúo(self):
		return self.tipo in [
			Carta.Tipo.CANGREJO,
			Carta.Tipo.BARCO,
			Carta.Tipo.PEZ,
			Carta.Tipo.NADADOR,
			Carta.Tipo.TIBURÓN
		]
	
	def esColeccionable(self):
		return self.tipo in [
			Carta.Tipo.CONCHA,
			Carta.Tipo.PULPO,
			Carta.Tipo.PINGUINO,
			Carta.Tipo.ANCLA
		]
	
	def esMultiplicador(self):
		return self.tipo in [
			Carta.Tipo.COLONIA,
			Carta.Tipo.FARO,
			Carta.Tipo.CARDUMEN,
			Carta.Tipo.CAPITÁN
		]

	def __str__(self):
		return f"Carta de {self.tipo.name.capitalize()} {self.color.name.lower().replace('_',' ')}"
	
	def __repr__(self):
		return f"Carta de {self.tipo.name.capitalize()} {self.color.name.lower().replace('_',' ')}"

	def __eq__(self, other):
		if not isinstance(other, Carta):
			return NotImplemented
		return self.tipo.value == other.tipo.value and self.color.value == other.color.value
	
	def __lt__(self, other):
		return (self.tipo.value < other.tipo.value) or (self.tipo.value == other.tipo.value and self.color.value < other.color.value)
	
	def __hash__(self):
		return hash((self.tipo, self.color))
	
	def aDiccionario(self):
		return {'tipo': self.tipo.value, 'color': self.color.value}

apodosCartas = {
	Carta.Tipo.CANGREJO: "Cjo",
	Carta.Tipo.BARCO: "Bco",
	Carta.Tipo.PEZ: "Pez",
	Carta.Tipo.NADADOR: "Ndr",
	Carta.Tipo.TIBURÓN: "Tbn",
	Carta.Tipo.CONCHA: "Con",
	Carta.Tipo.PULPO: "Plp",
	Carta.Tipo.PINGUINO: "Pgo",
	Carta.Tipo.ANCLA: "Anc",
	Carta.Tipo.COLONIA: "Col",
	Carta.Tipo.FARO: "Far",
	Carta.Tipo.CARDUMEN: "Cdm",
	Carta.Tipo.CAPITÁN: "Cpt",
	Carta.Tipo.SIRENA: "Sna"
}