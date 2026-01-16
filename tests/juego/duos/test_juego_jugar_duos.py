import pytest
from juego.carta import Carta
from juego.partida import PartidaDeOcéanos, JuegoException
from collections import Counter as Multiset

def test_SiSeInicióRonda_NoSePuedeJugarDúosAntesDeRobar():
	juego = PartidaDeOcéanos(cantidadDeJugadores=2)
	juego.iniciarRonda()
	
	with pytest.raises(JuegoException) as excepcion:
		juego.jugarDúoDeBarcos(Multiset())
	
	assert "No se puede jugar dúos sin antes haber robado" in str(excepcion.value)

def test_NoSePuedeJugarUnDúoDeCeroCartas():
	
	juego = PartidaDeOcéanos(cantidadDeJugadores=2)
	juego.iniciarRonda()
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(0,0)
	
	with pytest.raises(JuegoException) as excepcion:
		juego.jugarDúoDeBarcos(Multiset())
	
	assert "Se necesitan dos cartas para jugar un dúo" in str(excepcion.value)

def test_NoSePuedeJugarUnDúoDeUnaCarta():
	
	juego = PartidaDeOcéanos(cantidadDeJugadores=2)
	juego.iniciarRonda()
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(0,0)
	
	with pytest.raises(JuegoException) as excepcion:
		juego.jugarDúoDeBarcos(Multiset([Carta(Carta.Tipo.ANCLA, Carta.Color.BLANCO)]))
	
	assert "Se necesitan dos cartas para jugar un dúo" in str(excepcion.value)

def test_NoSePuedeJugarUnDúoDeMásDeDosCartas():
	
	juego = PartidaDeOcéanos(cantidadDeJugadores=2)
	juego.iniciarRonda()
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(0,0)
	
	with pytest.raises(JuegoException) as excepcion:
		juego.jugarDúoDeBarcos(Multiset([
			Carta(Carta.Tipo.ANCLA, Carta.Color.BLANCO),
			Carta(Carta.Tipo.ANCLA, Carta.Color.BLANCO),
			Carta(Carta.Tipo.ANCLA, Carta.Color.BLANCO)
	]))
	
	assert "Se necesitan dos cartas para jugar un dúo" in str(excepcion.value)
	
def test_NoSePuedeJugarUnDúoDeCartasQueNoSeanDeTipoDúo():
	
	juego = PartidaDeOcéanos(cantidadDeJugadores=2)
	juego.iniciarRonda()
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(0,0)
	
	with pytest.raises(JuegoException) as excepcion:
		juego.jugarDúoDeBarcos(Multiset([
			Carta(Carta.Tipo.ANCLA, Carta.Color.BLANCO),
			Carta(Carta.Tipo.ANCLA, Carta.Color.BLANCO)
	]))
	
	assert "Se necesitan cartas dúo para jugar un dúo" in str(excepcion.value)

def test_NoSePuedeJugarUnDúoDeCartasQueNoSeanDelMismoTipo():
	
	juego = PartidaDeOcéanos(cantidadDeJugadores=2)
	juego.iniciarRonda()
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(0,0)
	
	with pytest.raises(JuegoException) as excepcion:
		juego.jugarDúoDeBarcos(Multiset([
			Carta(Carta.Tipo.BARCO, Carta.Color.BLANCO),
			Carta(Carta.Tipo.PEZ, Carta.Color.BLANCO)
	]))
	
	assert "Se necesitan cartas del mismo tipo dúo para jugar un dúo" in str(excepcion.value)

def test_NoSePuedeJugarUnDúoDeCartasQueNoEsténEnLaManoDelJugador():
	
	juego = PartidaDeOcéanos(cantidadDeJugadores=2)
	juego.iniciarRonda()
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(0,0)
	
	with pytest.raises(JuegoException) as excepcion:
		juego.jugarDúoDeBarcos(Multiset([
			Carta(Carta.Tipo.BARCO, Carta.Color.BLANCO),
			Carta(Carta.Tipo.BARCO, Carta.Color.AZUL)
	]))
	
	assert "Las cartas seleccionadas no están en la mano" in str(excepcion.value)

def test_SiSeTieneUnDúo_AlJugarDúo_LasCartasDelDúoNoEstánEnLaMano():
	
	juego = PartidaDeOcéanos(cantidadDeJugadores=2)
	juego.iniciarRonda()
	juego._mazo[-1] = Carta(Carta.Tipo.BARCO,Carta.Color.AZUL)
	juego._mazo[-3] = Carta(Carta.Tipo.BARCO,Carta.Color.AMARILLO)
	
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(0,0)
	juego.pasarTurno()
	juego.robarDelDescarte(0)
	juego.pasarTurno()
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(0,0)
	
	
	juego.jugarDúoDeBarcos(Multiset([
		Carta(Carta.Tipo.BARCO,Carta.Color.AZUL),
		Carta(Carta.Tipo.BARCO,Carta.Color.AMARILLO)
	]))
	
	assert juego._estadosDeJugadores[0].mano.total() == 0
	
def test_SiSeTieneUnDúo_AlJugarDúo_ElRestoDeLaManoQuedaIgual():
	
	juego = PartidaDeOcéanos(cantidadDeJugadores=2)
	juego.iniciarRonda()
	juego._mazo[-1] = Carta(Carta.Tipo.BARCO,Carta.Color.AZUL)
	juego._mazo[-3] = Carta(Carta.Tipo.BARCO,Carta.Color.AMARILLO)
	
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(0,0)
	juego.pasarTurno()
	juego.robarDelDescarte(0)
	juego.pasarTurno()
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(0,0)
	juego.pasarTurno()
	cartaEnMano = juego._mazo[-1]
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(1,1)
	juego.pasarTurno()
	juego.robarDelDescarte(1)
	
	juego.jugarDúoDeBarcos(Multiset([
		Carta(Carta.Tipo.BARCO,Carta.Color.AZUL),
		Carta(Carta.Tipo.BARCO,Carta.Color.AMARILLO)
	]))
	
	assert juego._estadosDeJugadores[0].mano == Multiset([cartaEnMano])
	
def test_SiSeTieneUnDúo_AlJugarDúo_LasCartasDelDúoEstánEnLaZonaDeDúos():
	
	juego = PartidaDeOcéanos(cantidadDeJugadores=2)
	juego.iniciarRonda()
	juego._mazo[-1] = Carta(Carta.Tipo.BARCO,Carta.Color.AZUL)
	juego._mazo[-3] = Carta(Carta.Tipo.BARCO,Carta.Color.AMARILLO)
	
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(0,0)
	juego.pasarTurno()
	juego.robarDelDescarte(0)
	juego.pasarTurno()
	juego.verCartasParaRobarDelMazo()
	juego.robarDelMazo(0,0)
	
	
	juego.jugarDúoDeBarcos(Multiset([
		Carta(Carta.Tipo.BARCO,Carta.Color.AMARILLO),
		Carta(Carta.Tipo.BARCO,Carta.Color.AZUL)
	]))
	
	assert juego._estadosDeJugadores[0].zonaDeDúos == Multiset([(
		Carta(Carta.Tipo.BARCO,Carta.Color.AMARILLO),
		Carta(Carta.Tipo.BARCO,Carta.Color.AZUL)
	)])
	
	