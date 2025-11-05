=============================================================
    PROYECTO: BrickScript - Un Lenguaje para Juegos Retro
=============================================================

Desarrolladores:
Tomás Aristizábal Gómez
Juan Nicolás Chaparro Rodríguez
Andrés Felipe Chica Ospina

Este proyecto incluye el compilador que traduce el codigo BrickScript a un formato que la computadora entiende, y el motor de juego que lo ejecuta.

El runtime fue implementado para Windows con Python 2.7

-------------------------------------------------------------
                      COMO JUGAR
-------------------------------------------------------------

1. Abre una terminal de comandos (cmd.exe) y ubicate en la dirección principal del proyecto (esta dirección depende de en dónde hayas guardado los archivos).
2. Una vez estés situado en la dirección principal del proyecto, ejecuta los siguientes comandos para jugar:
    PARA EL SNAKE: .\jugar.bat Snake
    PARA EL TETRIS: .\jugar.bat TETRIS

Esto lo que va a hacer es ejecutar primero el compilador para la creación (en caso de que no existan aún) del archivo .json correspondiente al juego que seleccionaste.
Después, lo que hace es ejecutar el runtime que va a leer el respectivo .json creado para poder ejecutar el juego.

-------------------------------------------- 
            CONTROLES
--------------------------------------------

TETRIS:
        Cambiar la rotación de la figura: w
        Mover la figura hacia abajo: s
        Mover la figura a la derecha: d
        Mover la figura a la izquierda: a
        Poder Tsunami: t
        Poder Bomba: k

SNAKE:
        Mover la serpiente hacia arriba: w
        Mover la serpiente hacia abajo: s
        Mover la serpiente hacia la derecha: d
        Mover la serpiente hacia la izquierda: a

-------------------------------------------- 
            EVENTOS GENERALES
--------------------------------------------

ON_START: Este evento se encarga de iniciar el juego. Si el juego es el tetris, se encarga de hacer aparecer una pieza aleatoria al inicio del juego. De lo contrario,
          si el juego es el snake, este se encargará de hacer aparecer al jugador (la serpiente) y una fruta aleatoria al incio del juego.

ON_TICK: Se encarga del movimiento "generico" de cada juego. Si se trata del tetris, entonces se encarga del movimiento continuo hacia abajo de las piezas (la gravedad).
         Si el juego es el snake, se encarga de mantener el movimiento en la dirección a la que apunta la cabeza de la serpiente.

ON_KEY_UP: Se encarga del movimiento hacia arriba en caso del snake, en caso del tetris se encarga de cambiar la rotación de la figura.

ON_KEY_DOWN: Se encarga del movimiento hacia abajo de las figuras del tetris y la serpiente del snake.

ON_KEY_LEFT: Se encarga del movimiento hacia la izquierda de las figuras del tetris y la serpiente del snake.

ON_KEY_RIGHT: Se encarga del movimiento hacia la derecha de las figuras del tetris y la serpiente del snake.

ON_ESPEJO: Invierte los controles del juego durante 10 segundos. En el caso del juego snake este modo se activa cuando el jugador consume la fruta borojó; en el caso del
           juego tetris este modo se puede activar de manera aleatoria una vez que el jugador haya completado una fila.

-------------------------------------------- 
            EVENTOS TETRIS
--------------------------------------------

NOTA: Nosotros decidimos incluir dos "poderes" aleatorios para nuestro juego de tetris los cuales son "Tsunami" y "Bomba", estos se van a explicar en sus respectivos eventos,
      además que estos poderes pueden aparecer de manera aleatoria cada vez que el jugador completa una fila.

ON_LINE_CLEAR: Se encarga de que una vez que se haya completado una fila, la puntuación aumente y que la fila desaparezca.

ON_TSUNAMI: Se encarga de que cuando el jugador obtenga este poder de manera aleatoria y presione la tecla correspondiente, las dos últimas filas del tablero desaparecen.

ON_BOMB: Se encarga de que cuando el jugador obtenga este poder de manera aleatoria y presione la tecla correspondiente, va a ocurrir una especie de "explosión" en un radio de
         5x5 en el centro del tablero con el fin de abrir espacio para el jugador.

-------------------------------------------- 
            EVENTOS SNAKE
--------------------------------------------

NOTA: Nosotros decidimos incluir 3 frutas adicionales aparte de la tradicional (manzana) que se encarga de hacer crecer a la serpiente. Sus funcionalidades se explicaran en
      sus respectivos eventos.

ON_COLLISION_WALL: Se encarga de terminar el juego en caso de que la serpiente se choque con alguna pared.

ON_COLLISION_SELF: Se encarga de terminar el juego en caso de que la serpiente se choque con su mismo cuerpo.

ON_EAT_FOOD: Se encarga de aumentar el tamaño de la serpiente cuando se consume una fruta (excepto con la fruta venenosa), también se encarga de volver a hacer aparecer una
             fruta aleatoria y de aumentar la puntuación del juego.

ON_EAT_VENOM: Se encarga de disminuir el tamaño de la serpiente cuando se come la fruta venenosa.

ON_EAT_SLOW: Se encarga de disminuir la velocidad de movimiento de la serpiente durante un lapso de 10 segundos al consumir la fruta chontaduro.