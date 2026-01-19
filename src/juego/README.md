
# Módulo de Juego

## Cartas
La clase [`Carta`](https://github.com/AugustoNicola/oceanos-juego/blob/main/src/juego/carta.py) define la estructura de una carta del juego. Las cartas son estructuras muy sencillas, que solo tienen un `tipo` y un `color`. Ambos atributos son [Enums](https://docs.python.org/3/library/enum.html) con los valores válidos del juego (por ejemplo, `Carta.Tipo.CANGREJO` y `Carta.Color.NARANJA`).

## Partida de Océanos
La clase [`PartidaDeOcéanos`](https://github.com/AugustoNicola/oceanos-juego/blob/main/src/juego/partida.py) modela el estado y acciones posibles a lo largo de una única partida del juego (con múltiples rondas) entre 2-4 jugadores. Tiene métodos para realizar las acciones correspondientes en cada momento, y expone las propiedades que el jugador actual debería concoer en una partida real.

### Métodos de acción
Los métodos disponibles públicamente que "hacen algo en el juego" son los siguientes:

* `iniciarRonda()`: inicia una nueva ronda desde cero.
* `robarDelDescarte(índicePilaDeDescarte)`: el jugador activo roba la carta superior de la pila de descarte indicada.
* `verCartasParaRobarDelMazo()`: el jugador activo decide que va a robar cartas del mazo, por lo que se le deja ver las dos cartas superiores del mazo. Esta acción obliga al jugador a robar del mazo.
* `robarDelMazo(índiceDeCartaARobar, índiceDePilaDondeDescartar)`: el jugador activo elige cuál de las cartas vistas quedarse, y en qué pila de descarte dejar la otra.
* `jugarDúoDePeces(cartasAJugar)`: el jugador activo juega un dúo de peces desde su mano.
* `jugarDúoDeBarcos(cartasAJugar)`: el jugador activo juega un dúo de barcos desde su mano.
* `jugarDúoDeCangrejos(cartasAJugar, pilaDeDescarteARobar, índiceDeCartaARobar)`: el jugador activo juega un dúo de cangrejos desde su mano, y roba la carta elegida.
* `jugarDúoDeNadadorYTiburón(cartasAJugar, jugadorARobar)`: el jugador activo juega un dúo de nadador y tiburón desde su mano, y roba una carta al azar de la mano del jugador elegido.
* `pasarTurno()`: el jugador activo pasa de turno.
* `decirBasta()`: el jugador activo dice ¡Basta!. La ronda termina y cada jugador suma el puntaje de ronda.
* `decirÚltimaChance()`: el jugador activo dice ¡Última Chance!. Su turno termina y la ronda terminará cuando vuelva a ser su turno.

La clase entiende qué ordenes de estos eventos son válidos y envía un error en caso de intentarse realizar una acción inválida (como pasar de turno antes de robar, o descartar una carta en una pila no existente).

Estos métodos NO DEBEN SER USADOS DESDE LOS [JUGADORES](https://github.com/AugustoNicola/oceanos-juego/tree/main/src/jugador), sino que serán invocados por el [`AdministradorDeJuego`](https://github.com/AugustoNicola/oceanos-juego/tree/main/src/administrador) acorde a lo retornado por cada uno de los métodos de la interfaz de [`JugadorBase`](https://github.com/AugustoNicola/oceanos-juego/blob/main/src/jugador/base.py).

### Atributos públicos
Se exponen los siguientes atributos y métodos públicos (son públicos porque su nombre no arranca con `_`):

* `topeDelDescarte`: devuelve una tupla con la carta en el tope de cada pila de descarte (o `None` si la pila está vacía)
* `cantidadDeCartasEnDescarte`: devuelve una tupla con la cantidad de cartas en cada pila de descarte
* `cantidadDeCartasEnManoDelJugador(j)`: devuelve la cantidad de cartas en la mano del jugador `j` 
* `cantidadDeCartasEnMazo`: devuelve la cantidad de cartas en el mazo
* `zonaDeDúosDelJugador(j)`: devuelve la zona de dúos (un `Multiset` de tuplas de cartas) del jugador `j`
* `zonaDeDúos`: devuelve la zona de dúos (un `Multiset` de tuplas de cartas) del jugador activo
* `mano`: devuelve la mano (un `Multiset` de Cartas) del jugador activo
* `puntajeDeRonda`: devuelve la cantidad de puntos de ronda que el jugador activo tiene actualmente
* `puntajes`: devuelve un arreglo con el puntaje de partida (sin contar la ronda en curso) de cada jugador
* `puntajeParaGanar`: devuelve el puntaje necesario para terminar la partida
* `jugadorQueDijoÚltimaChance`: devuelve el jugador que dijo ¡Última chance!, en caso de haberse cantado. Si no, devuelve `None`
* `últimaChanceEnCurso()`: devuelve si se ha cantado o no ¡Última chance!
* `últimaChanceGanada()`: si la ronda terminó por ¡Última chance!, devuelve si la apuesta fue ganada o no. En caso contrario, devuelve `None`
* `rondaAnulada()`: devuelve si la ronda terminó por quedar cero cartas en el mazo al iniciar un turno

Estos métodos y atributos están pensados ser usados desde los Jugadores, ya que conforman información que los jugadores tienen en una partida real.

