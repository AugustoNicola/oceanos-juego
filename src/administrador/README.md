# Módulo Administrador

## Administrador de Juego
La clase [`AdministradorDeJuego`](https://github.com/AugustoNicola/oceanos-juego/blob/main/src/administrador/administrador_de_juego.py) actúa como puente entre instancias de [`PartidaDeOcéanos`](https://github.com/AugustoNicola/oceanos-juego/blob/main/src/juego/partida.py) y los [Jugadores](https://github.com/AugustoNicola/oceanos-juego/blob/main/src/jugador/README.md). Su tarea es invocar los métodos correspondientes que los Jugadores implementan y usar sus respuestas para resolver las diferentes fases del juego con llamadas a métodos de `PartidaDeOcéanos`.

### Cómo usar

#### Desde la terminal

Desde `src/`, correr `python -m administrador.administrador_de_juego <nombre_jugador1> <nombre_jugador1> <...>`, con los `<nombre_jugadorN>` reemplazados por los [nombres de jugadores](https://github.com/AugustoNicola/oceanos-juego/tree/main/src/jugador) a usar.

#### Desde otro archivo

Esta clase espera ser creada con un arreglo de nombres de los jugadores que van a jugar (es decir, se invoca como `AdministradorDeJuego(nombresDeJugadores=['randybot', 'sirena_enjoyer'])`), y expone un método `jugarPartida()`. Cuando este método es llamado, el administrador se encarga de simular una partida de principio a fin entre los jugadores, y retorna la posición del jugador ganador. `jugarPartida()` puede ser llamada múltiples veces para jugar muchas partidas.

### Verbosidad de loggeo

El parámetro `verbosidad` en el constructor de la clase controla si se imprime en pantalla texto sobre cada acción ocurrida en la partida. Los valores posibles son `Verbosidad.NADA` (no imprimir nada), `Verbosidad.JUGADOR` (imprimir sólo información pública) y `Verbosidad.OMNISCIENTE` (imprimir toda la información).

### Estadísticas de juego

El administrador también recolecta diversas estadísticas de las partidas:

* `_cantidadDeCartasPorJugadorPorTipo`
* `_partidasGanadasPorJugador`
* `_puntosPorJugadorPorRonda`
* `_dúosJugadosPorJugadorPorTipo`
* `_dúosEnManoPorJugadorPorTipo` 
* `_motivosFinDeRonda`
* `_motivosFinDeRondaPorJugador`

Esta información puede ser accedida en cualquier momento a través de los atributos privados de la clase. Se usa por ejemplo en el [sistema de Matchups](https://github.com/AugustoNicola/oceanos-juego/blob/main/src/matchup/README.md).

## Tipos de Acción
Para que los Jugadores puedan comunicarle al administrador qué tipo de acción desean realizar en cada momento de la partida, se utiliza la clase [`Acción`](https://github.com/AugustoNicola/oceanos-juego/blob/main/src/administrador/acción.py), es un [Enum](https://docs.python.org/3/library/enum.html) con los siguientes valores:

* `Acción.Robo.DEL_MAZO`: representa la acción de robar del mazo
* `Acción.Robo.DEL_DESCARTE_0`: representa la acción de robar de la pila de descarte izquierda (índice 0)
* `Acción.Robo.DEL_DESCARTE_1`: representa la acción de robar de la pila de descarte derecha (índice 1)
* `Acción.Dúos.NO_JUGAR`: representa la intención de no jugar más dúos en esta ronda
* `Acción.Dúos.JUGAR_PECES`: representa la acción de jugar un dúo de peces de la mano
* `Acción.Dúos.JUGAR_BARCOS`: representa la acción de jugar un dúo de barcos de la mano
* `Acción.Dúos.JUGAR_CANGREJOS`: representa la acción de jugar un dúo de cangrejos de la mano
* `Acción.Dúos.JUGAR_NADADOR_Y_TIBURÓN`: representa la acción de jugar un dúo de nadador y tiburón de la mano
* `Acción.FinDeTurno.PASAR_TURNO`: representa la intención de pasar el turno normalmente
* `Acción.FinDeTurno.DECIR_BASTA`: representa la acción de decir ¡Basta!
* `Acción.FinDeTurno.ÚLTIMA_CHANCE`:  representa la acción de decir ¡Última Chance!

Los métodos de los Jugadores que el administrador invoca durante el juego usualmente devuelven alguna `Acción` que tenga sentido para ese método (por ejemplo, `decidirAcciónDeRobo` debe devolver algún valor de `Acción.Robo`), además de más información que sea necesaria según el caso (por ejemplo, a qué jugador se le quiere robar con un dúo de nadador y tiburón).

## Sistema de Eventos
En una partida real, ocurren situaciones en las cuales los jugadores obtienen información por acciones fuera de su turno, pero que no es inferible cuando es su turno (por ejemplo, si alguien descarta una Sirena y otra persona la tapa con un Cangrejo, cuando sea mi turno no tengo derecho a ver qué cartas hay abajo del Cangrejo, pero "sé" que hay una Sirena abajo si presté atención). Para modelar esto, el `AdministradorDeJuego` les provee a los Jugadores acceso a una lista de eventos.

El atributo `_eventos` es un arreglo de objetos de tipo [`Evento`](https://github.com/AugustoNicola/oceanos-juego/blob/main/src/administrador/evento.py). Cada `Evento` es una tripla con campos:

* `jugador`: el número del jugador que generó el evento
* `acción`: el tipo de `Acción` del evento
* `parámetros`: un diccionario con información adicional según el tipo de acción. Estos son los parámetros de cada acción registrada:
  * `Acción.Robo.DEL_MAZO`: `"cartaDescartada"` (la `Carta` que se envió al descarte), `"pilaDondeDescartó"` (índice de la pila, `0` o `1`), y `"_cartaRobada"` (la `Carta` que se llevó a la mano). LOS PRIMEROS DOS PUEDEN SER `None` SI NO SE DESCARTÓ CARTA! (lo cual ocurre cuando solo queda una carta en el mazo)
  * `Acción.Robo.DEL_DESCARTE_0|1`: `"cartaRobada"` (la `Carta` que se retiró del descarte)
  * `Acción.Dúos.JUGAR_PECES`: `"cartasJugadas"` (tupla con dos `Carta`s) y `"_cartaRobada"` (la `Carta` que robó del mazo al usar el dúo)
  * `Acción.Dúos.JUGAR_BARCOS`: `"cartasJugadas"` (tupla con dos `Carta`s)
  * `Acción.Dúos.JUGAR_CANGREJOS`: `"cartasJugadas"` (tupla con dos `Carta`s), `"pilaDondeRobó"` (índice de la pila, 0 o 1), y `"_cartaRobada"` (la `Carta` robada del descarte con el dúo)
  * `Acción.Dúos.JUGAR_NADADOR_Y_TIBURÓN`: `"cartasJugadas"` (tupla con dos `Carta`s), `"jugadorRobado"` (número de jugador) y `"_cartaRobada"` (la `Carta` que se le robó al jugador robado).
  * `Acción.Dúos.PASAR_TURNO`: el diccionario es `None`, no hay parámetros.
  * `Acción.Dúos.DECIR_BASTA`: el diccionario es `None`, no hay parámetros.
  * `Acción.Dúos.PASAR_ÚLTIMA_CHANCE`: el diccionario es `None`, no hay parámetros.

Muy importante: los parámetros que empiezan con barra baja (`_`) contienen información secreta que no todo jugador debería poder ver. Hacer el favor de asegurarse que tienen permiso para verlos antes de usarlos (por ejemplo, puedo ver qué carta se robó en un evento de `Acción.Dúos.JUGAR_NADADOR_Y_TIBURÓN` solo si soy el jugador que robó o el robado).

La lista de Eventos se limpia al inicio de cada ronda. Es responsabilidad de los Jugadores calcular qué eventos son nuevos y cuáles ya fueron vistos antes.