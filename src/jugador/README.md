# Módulo Jugador

Para que un jugador pueda entenderse con el [`AdministradorDeJuego`](https://github.com/AugustoNicola/oceanos-juego/blob/main/src/administrador/README.md), se necesita que [subclasifique](https://www.w3schools.com/python/python_inheritance.asp) la clase [`JugadorBase`](https://github.com/AugustoNicola/oceanos-juego/blob/main/src/jugador/base.py). Esta clase define los métodos que `AdministradorDeJuego` invoca sobre cada jugador para resolver las acciones de juego (cómo se quiere robar, si se quieren jugar dúos, cómo se pasa de ronda, etc.). Por supuesto, además de implementar estos métodos necesarios, un jugador puede definir tantas variables internas y métodos auxiliares como sean necesarios.

## Nombre de jugador

Todo jugador define su nombre a través de `@registrarComo("un_nombre")`. Este nombre es el que esperan tanto el `AdministradorDeJuego` como la [interfaz web](https://github.com/AugustoNicola/oceanos-interfaz).

## Métodos a Implementar

### Método `decidirAcciónDeRobo()`

Este método se invoca al principio de cada turno para que el Bot elija cuál de las tres acciones de robo posible quiere realizar (`Acción.Robo.DEL_MAZO` o `Acción.Robo.DEL_DESCARTE_0|1`). Recordar que:
* Robar del descarte NO SIEMPRE ES POSIBLE: hay que revisar si hay cartas en la pila de descarte donde se quiere robar.

### Método `decidirCómoRobarDelMazo(opcionesDeRobo)`

Este método se invoca al principio del turno si el Bot eligió robar del mazo cuando se llamó a `decidirAcciónDeRobo()`. El Bot tiene que tomar las dos decisiones involucradas con robar del mazo: elegir cuál de las dos cartas de `opcionesDeRobo` se queda en la mano, y en cuál de las dos pilas de descarte se descarta la carta no elegida. Estas decisiones son lo que el método debería retornar, con una tupla de la forma `(indiceDeCartaARobar, indiceDePilaDondeDescartar)`. Recordar que:

* No siempre `opcionesDeRobo` tiene dos cartas: podría pasar que se esté intentando robar la única carta que queda del mazo. Revisar con `len(opcionesDeRobo) > 1`
* No siempre es posible elegir una pila de descarte para descartar la carta no robada. Recordar que si una pila de descarte está vacía y la otra no, es obligatorio descartar en esa pila. Revisar con `_juego.cantidadDeCartasEnDescarte`.
* No siempre es necesario descartar una carta: podría pasar que se esté intentando robar la única carta que queda del mazo, y en ese caso no hay que descartar nada. Si esto ocurre, no importa el valor de `indiceDePilaDondeDescartar` (puede ser `None` incluso).

### Método `decidirAcciónDeDúos()`

Este método se invoca durante la fase de dúos (luego de robar) para que el Bot elija qué dúo (si alguno) desea jugar inmediatamente. Se espera como respuesta una tripla de la pinta `(acciónElegida, cartasAJugar, parámetrosDelDúo)`, donde `acciónElegida` es una `Acción.Dúos`, `cartasAJugar` es un `Multiset` con las cartas a jugar, y `parámetrosDelDúo` son los parámetros de la siguiente manera:
* Para dúos de peces y barcos, es `None` (ya que estos dúos no requieren parámetros)
* Para dúos de cangrejos, es una 1-upla `(pilaElegida)`, donde `pilaElegida` es el índice de la pila donde se roba. La decisión de qué carta de dicha pila se va a robar queda delegada a `decidirQuéRobarConDúoDeCangrejos`.
* Para dúos de nadador y tiburón, es una 1-upla `(jugadorARobar)`, donde `jugadorARobar` es el índice del jugador a robar.

Esta fase es la más compleja por la cantidad de cosas que pueden hacerse, y es importante asegurarse de que los parámetros enviados son válidos:

* `cartasAJugar` siempre debe ser un `Multiset` que contenga exactamente dos cartas, que sean del tipo de dúo elegido, y que efectivamente estén en la mano. Se puede usar el auxiliar `_buscarDúoParaJugar`.
* Cangrejos: asegurarse de que la `pilaElegida` tenga al menos `índiceElegido + 1` cartas.
* Nadador&Tiburón: asegurarse de que el jugador elegido no sea uno mismo...

El método se invoca reiteradas veces sobre el Bot hasta que el Bot responde `Acción.Dúos.NO_JUGAR`, y entonces se pasa a la fase de fin de ronda.

### Método `decidirQuéRobarConDúoDeCangrejos(descarteElegido)`

Este método se invoca si el Bot eligió jugar un dúo de cangrejos cuando se llamó a `decidirAcciónDeRobo()`. El Bot tiene que tomar la decisión de qué carta llevarse de la pila de descarte anteriormente elegida, devolviendo el índice de la carta elegida. El parámetro `descarteElegido` es una copia de la pila de descarte elegida (donde la carta de más arriba es la del índice más alto numéricamente).


### Método `decidirAcciónDeFinDeTurno()`

Este método se invoca al final de cada turno para que el Bot elija cuál de las tres acciones para terminar su turno quiere realizar (`Acción.FinDeTurno.PASAR_TURNO`, `Acción.FinDeTurno.DECIR_BASTA` o `Acción.FinDeTurno.DECIR_ÚLTIMA_CHANCE`). Recordar que:
* Para poder decir ¡Basta! o ¡Última Chance!, es necesario tener al menos siete puntos. Se puede revisar la cantidad de puntos con `_juego.puntajeDeRonda`. Además, tiene que no haber un ¡Última chance! en curso, lo cual se puede revisar con `_juego.últimaChanceEnCurso()`.

### Método `configurarInicioDeRonda(cartasInicialesDelDescarte)`

Este método se invoca al principio de cada ronda para que el Bot pueda realizar los cálculos que quiera de acuerdo al estado de la partida al principio de la ronda. Se hace pública la información de qué dos cartas hay en el descarte al iniciar la ronda. No se necesita devolver nada en particular.

### Método `configurarFinDeRonda(manos, puntajesDeRonda)`

Este método se invoca al final de cada ronda para que el Bot pueda realizar los cálculos que quiera de acuerdo al estado de la partida luego de jugar la ronda. Además, como en esta fase los jugadores tienen que revelar sus manos y contar sus puntajes de ronda, esta información se hace pública para todos los Jugadores a través de los parámetros pasados. No se necesita devolver nada en particular.

### Método `configurarInicioDeTurno()`

Este método se invoca al principio del turno del Bot. Puede ser un buen momento para revisar el listado de eventos. No se necesita devolver nada en particular.


### Auxiliares

La clase de `JugadorBase` ya implementa algunos métodos auxiliares para facilitar tareas comunes, como `_buscarDúoParaJugar`.

## Jugadores Implementados

Ya están implementados varios Jugadores con distintas ideas. Podés probarlos por terminal con el [administrador de juego](../administrador/README.md), con el [sistema de matchups](../matchup/README.md), y ahora también a través de la [interfaz web](https://github.com/AugustoNicola/oceanos-interfaz)!