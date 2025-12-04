# -*- coding: utf-8 -*-

import sys
import json
import os
import time
import random
import Tkinter as tk

class Juego:
    def __init__(self, datos_juego, root):
        self.datos_juego = datos_juego
        self.tipo_juego = self.datos_juego.get('tipo_juego', 'TETRIS')
        config = self.datos_juego.get('config', {})
        self.ancho = config.get('grid_size', [10, 20])[0]
        self.alto = config.get('grid_size', [10, 20])[1]
        self.grid = [[None for _ in range(self.ancho)] for _ in range(self.alto)]
        self.puntuacion = 0
        self.probabilidad_poderes = 0.5
        self.juego_terminado = False
        self.modo_espejo = False
        self.tiempo_fin_espejo = 0.0
        self.probabilidad_espejo = 0.5
        
        if self.tipo_juego == 'TETRIS':
            self.pieza_actual = None
            self.pieza_x, self.pieza_y, self.pieza_rotacion = 0, 0, 0
            self.velocidad_gravedad = 0.4
            self.poderes_tetris = []
        
        if self.tipo_juego == 'SNAKE':
            self.serpiente_cuerpo = []
            self.serpiente_direccion = (1, 0)
            self.posicion_comida = None
            self.velocidad_base_snake = 0.15
            self.velocidad_gravedad = self.velocidad_base_snake
            self.fruta_actual = "@@" 
            self.modo_lento = False
            self.tiempo_fin_lento = 0.0
        
        self.timer_gravedad = 0
        self.ejecutar_evento('ON_START')

        # Configuración de Tkinter
        self.root = root
        self.tamano_celda = 20 # pixeles
        canvas_ancho = self.ancho * self.tamano_celda + 20
        canvas_alto = self.alto * self.tamano_celda + 20

        self.canvas = tk.Canvas(root, width=canvas_ancho, height=canvas_alto, bg='black')
        self.canvas.pack()

        # Panel de información a la derecha
        self.info_frame = tk.Frame(root, bg='black')
        self.info_frame.pack(side=tk.RIGHT, padx=10, pady=10, anchor='n')
        self.punt_label = tk.Label(self.info_frame, text="PUNTUACIÓN: 0", fg='white', bg='black', font=('Courier', 12))
        self.punt_label.pack(anchor='w')
        self.controls_label = tk.Label(self.info_frame, text="CONTROLES:\nWASD\n'q': Salir", fg='white', bg='black', font=('Courier', 10), justify=tk.LEFT)
        self.controls_label.pack(anchor='w', pady=(10,0))

        self.poderes_label = tk.Label(self.info_frame, text="", fg='yellow', bg='black', font=('Courier', 10), justify=tk.LEFT)
        self.poderes_label.pack(anchor='w', pady=(10,0))

        self.efectos_label = tk.Label(self.info_frame, text="", fg='cyan', bg='black', font=('Courier', 10), justify=tk.LEFT)
        self.efectos_label.pack(anchor='w', pady=(10,0))

        #Guía de frutas para el Snake
        if self.tipo_juego == 'SNAKE':
            tk.Label(self.info_frame, text="GUIA DE FRUTAS:", fg='cyan', bg='black', font=('Courier', 10, 'bold')).pack(anchor='w', pady=(10,0))
        # Manzana @@ → rojo
        self.fruta_manzana = tk.Label(self.info_frame, text="Manzana", fg='#FF0000', bg='black', font=('Courier', 10))
        self.fruta_manzana.pack(anchor='w')
        # Borojo ?? → naranja
        self.fruta_borojo = tk.Label(self.info_frame, text="Borojo", fg='#FF8000', bg='black', font=('Courier', 10))
        self.fruta_borojo.pack(anchor='w')
        # Chontaduro && → dorado
        self.fruta_chontaduro = tk.Label(self.info_frame, text="Chontaduro", fg='#FFD700', bg='black', font=('Courier', 10))
        self.fruta_chontaduro.pack(anchor='w')
        # Venenosa !! → morado
        self.fruta_venenosa = tk.Label(self.info_frame, text="Venenosa", fg='#8B008B', bg='black', font=('Courier', 10))
        self.fruta_venenosa.pack(anchor='w')
        # Vincular teclas
        root.bind('<Key>', self.manejar_input)
        self.root.protocol('WM_DELETE_WINDOW', self.salir)

        # Colores para el Tetris
        self.colores_tetris = {
            'FIGURA_LINEA': '#0EC2E6', 
            'FIGURA_CUADRO': '#F1F505',  
            'FIGURA_T': '#A020F0',  
            'FIGURA_S': '#00FF00',  
            'FIGURA_Z': '#F5023B',  
            'FIGURA_PISTOLA_INVERSA': '#050DF5',  
            'FIGURA_PISTOLA_DERECHA': '#FFA500'   
        }

        # Iniciar bucle del juego
        self.ultima_actualizacion = time.time()
        self.actualizar()
    
    def manejar_input(self, event):
        key = event.char.lower()
        if key == 'q':
            self.juego_terminado = True
            self.root.quit()

        elif self.tipo_juego == 'TETRIS':
            if not self.modo_espejo:
                if key == 'w': self.ejecutar_evento('ON_KEY_UP')
                elif key == 's': self.ejecutar_evento('ON_KEY_DOWN')
                elif key == 'a': self.ejecutar_evento('ON_KEY_LEFT')
                elif key == 'd': self.ejecutar_evento('ON_KEY_RIGHT')
                elif key == 't': self.ejecutar_evento('ON_TSUNAMI')
                elif key == 'k': self.ejecutar_evento('ON_BOMB')
            else:
                if key == 'w': self.ejecutar_evento('ON_KEY_DOWN')
                elif key == 's': self.ejecutar_evento('ON_KEY_UP')
                elif key == 'a': self.ejecutar_evento('ON_KEY_RIGHT')
                elif key == 'd': self.ejecutar_evento('ON_KEY_LEFT')
                elif key == 't': self.ejecutar_evento('ON_TSUNAMI')
                elif key == 'k': self.ejecutar_evento('ON_BOMB')
        elif self.tipo_juego == 'SNAKE':
            if not self.modo_espejo:
                if key == 'w': self.snake_cambiar_direccion('UP')
                elif key == 's': self.snake_cambiar_direccion('DOWN')
                elif key == 'a': self.snake_cambiar_direccion('LEFT')
                elif key == 'd': self.snake_cambiar_direccion('RIGHT')
            else:
                if key == 'w': self.snake_cambiar_direccion('DOWN')
                elif key == 's': self.snake_cambiar_direccion('UP')
                elif key == 'a': self.snake_cambiar_direccion('RIGHT')
                elif key == 'd': self.snake_cambiar_direccion('LEFT')



    def dibujar(self):
        self.canvas.delete("all")
        # Dibujar borde del área de juego
        self.canvas.create_rectangle(5, 5,
                                     self.ancho * self.tamano_celda + 5,
                                     self.alto * self.tamano_celda + 5,
                                     outline='white', width=2)
        if self.tipo_juego == 'TETRIS':
            # Dibujar celdas fijas y pieza actual con colores
            for y in range(self.alto):
                for x in range(self.ancho):
                    pieza_nombre = self.grid[y][x]
                    x1 = x * self.tamano_celda + 5
                    y1 = y * self.tamano_celda + 5
                    x2 = x1 + self.tamano_celda
                    y2 = y1 + self.tamano_celda

                    color = 'black'
                    outline = 'gray'

                    if pieza_nombre is not None:
                        # Celda fija: usar color del tipo de pieza
                        color = self.colores_tetris.get(pieza_nombre, '#FFFFFF')
                    elif self.pieza_actual:
                        # Ver si esta celda pertenece a la pieza actual
                        y_loc = y - self.pieza_y
                        x_loc = x - self.pieza_x
                        matriz_pieza = self.pieza_actual[self.pieza_rotacion]
                        if (0 <= y_loc < len(matriz_pieza) and
                            0 <= x_loc < len(matriz_pieza[0]) and
                            matriz_pieza[y_loc][x_loc] == 1):
                            color = self.colores_tetris.get(self.nombre_pieza_actual, '#AAAAAA')
                            outline = 'white'

                    if color != 'black':
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline)

        elif self.tipo_juego == 'SNAKE':
            # Dibujar serpiente y comida
            for y in range(self.alto):
                for x in range(self.ancho):
                    x1 = x * self.tamano_celda + 5
                    y1 = y * self.tamano_celda + 5
                    x2 = x1 + self.tamano_celda
                    y2 = y1 + self.tamano_celda

                    color = 'black'
                    outline = 'gray'

                    # Dibujar cuerpo de la serpiente
                    if (x, y) in self.serpiente_cuerpo:
                        idx = self.serpiente_cuerpo.index((x, y))
                        if idx == 0:
                            color = '#FFFF00'  # cabeza
                        else:
                            color = '#00FF00'  # cuerpo

                    # Dibujar comida
                    elif self.posicion_comida and (x, y) == self.posicion_comida:
                        if self.fruta_actual == '@@':
                            color = '#FF0000'   # manzana
                        elif self.fruta_actual == '??':
                            color = '#FF8000'   # borojo
                        elif self.fruta_actual == '&&':
                            color = '#FFD700'   # chontaduro
                        elif self.fruta_actual == '!!':
                            color = '#8B008B'   # venenosa

                    if color != 'black':
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline)

        # ACTUALIZAR PANEL DE INFORMACIÓN
        self.punt_label.config(text="PUNTUACIÓN: {}".format(self.puntuacion))

        # Poderes (solo Tetris)
        poderes_texto = ""
        if self.tipo_juego == "TETRIS":
            if self.poderes_tetris:
                if "tsunami" in self.poderes_tetris:
                    poderes_texto += "TSUNAMI (T)\n"
                if "bomba" in self.poderes_tetris:
                    poderes_texto += "BOMBA (K)\n"
            else:
                poderes_texto = "No tienes poderes"
        self.poderes_label.config(text=poderes_texto)

        # Efectos activos
        efectos_texto = ""
        if self.modo_espejo:
            tiempo_restante = max(0, self.tiempo_fin_espejo - time.time())
            efectos_texto += "Modo espejo: INVERTIDO ({:.1f}s)\n".format(tiempo_restante)
        if self.tipo_juego == "SNAKE" and self.modo_lento:
            tiempo_restante = max(0, self.tiempo_fin_lento - time.time())
            efectos_texto += "Modo lento: ACTIVO ({:.1f}s)\n".format(tiempo_restante)
        self.efectos_label.config(text=efectos_texto)

        # Mostrar/ocultar guía de frutas (Solo Snake)
        if self.tipo_juego == "SNAKE":
            self.fruta_manzana.pack()
            self.fruta_borojo.pack()
            self.fruta_chontaduro.pack()
            self.fruta_venenosa.pack()
        else:
            self.fruta_manzana.pack_forget()
            self.fruta_borojo.pack_forget()
            self.fruta_chontaduro.pack_forget()
            self.fruta_venenosa.pack_forget()

    def ejecutar_evento(self, nombre_evento):
        if nombre_evento in self.datos_juego['events']:
            for accion in self.datos_juego['events'][nombre_evento]:
                verbo, objeto = accion.get('accion'), accion.get('objeto')
                
                if verbo == 'INCREASE_SCORE': self.puntuacion += int(objeto)
                if verbo == 'GAME_OVER': self.juego_terminado = True

                if self.tipo_juego == 'TETRIS':
                    if verbo == 'SPAWN': self.tetris_spawn_pieza()
                    if verbo == 'MOVE': self.tetris_mover_pieza(accion['params'][0])
                    if verbo == 'ROTATE': self.tetris_rotar_pieza()
                    if verbo == 'DESTROY_ROW': self.tetris_tsunami()
                    if verbo == 'EXPLODE': self.tetris_bomba()
                
                if self.tipo_juego == 'SNAKE':
                    if verbo == 'SPAWN' and objeto == 'PLAYER': self.snake_spawn_jugador(accion)
                    if verbo == 'SPAWN' and objeto == 'FOOD': self.snake_spawn_comida()
                    if verbo == 'MOVE' and objeto == 'PLAYER': self.snake_mover_jugador()
                    if verbo == 'GROW' and objeto == 'PLAYER': self.snake_crecer()
                    if verbo == 'SHRINK' and objeto == 'PLAYER': self.snake_encoger()

    def tetris_spawn_pieza(self):
        nombre_pieza = random.choice(self.datos_juego['shapes'].keys())
        self.pieza_actual = self.datos_juego['shapes'][nombre_pieza]
        self.nombre_pieza_actual = nombre_pieza
        self.pieza_x = self.ancho // 2 - 2
        self.pieza_y = 0
        self.pieza_rotacion = 0
        if self.tetris_verificar_colision(self.pieza_x, self.pieza_y, self.pieza_rotacion):
            self.juego_terminado = True
    
    def tetris_mover_pieza(self, direccion):
        if not self.pieza_actual: return
        dx, dy = 0, 0
        if direccion == 'LEFT': dx = -1
        elif direccion == 'RIGHT': dx = 1
        elif direccion == 'DOWN': dy = 1
        if not self.tetris_verificar_colision(self.pieza_x + dx, self.pieza_y + dy, self.pieza_rotacion):
            self.pieza_x += dx
            self.pieza_y += dy
        elif dy > 0:
            self.tetris_fijar_pieza()

    def tetris_rotar_pieza(self):
        if not self.pieza_actual: return
        nueva_rotacion = (self.pieza_rotacion + 1) % len(self.pieza_actual)
        if not self.tetris_verificar_colision(self.pieza_x, self.pieza_y, nueva_rotacion):
            self.pieza_rotacion = nueva_rotacion

    def tetris_fijar_pieza(self):
        if not self.pieza_actual or not self.nombre_pieza_actual:
            return
        matriz_pieza = self.pieza_actual[self.pieza_rotacion]
        for y_offset, fila in enumerate(matriz_pieza):
            for x_offset, celda in enumerate(fila):
                if celda == 1:
                    if 0 <= self.pieza_y + y_offset < self.alto and 0 <= self.pieza_x + x_offset < self.ancho:
                        self.grid[self.pieza_y + y_offset][self.pieza_x + x_offset] = self.nombre_pieza_actual
        self.pieza_actual = None
        self.nombre_pieza_actual = None
        self.tetris_limpiar_lineas()
        self.ejecutar_evento('ON_START')

    def tetris_verificar_colision(self, x, y, rotacion):
        if not self.pieza_actual: return False
        matriz_pieza = self.pieza_actual[rotacion]
        for y_offset, fila in enumerate(matriz_pieza):
            for x_offset, celda in enumerate(fila):
                if celda == 1:
                    nuevo_x, nuevo_y = x + x_offset, y + y_offset
                    if not (0 <= nuevo_x < self.ancho and 0 <= nuevo_y < self.alto):
                        return True
                    if self.grid[nuevo_y][nuevo_x] is not None:
                        return True
        return False

    def tetris_limpiar_lineas(self):
        nuevo_grid = []
        lineas_limpias = 0
        for fila in self.grid:
            if all(celda is not None for celda in fila):
                lineas_limpias += 1
            else:
                nuevo_grid.append(fila)
        if lineas_limpias > 0:
            # Añadir filas vacías arriba
            vacio = [None] * self.ancho
            self.grid = [vacio[:] for _ in range(lineas_limpias)] + nuevo_grid
            for _ in range(lineas_limpias):
                self.ejecutar_evento('ON_LINE_CLEAR')
            self.generar_poderes_tetris()
            self.funcion_modo_espejo()
    
    def tetris_tsunami(self):
        if "tsunami" in self.poderes_tetris:
            nuevo_grid = [fila for fila in self.grid[:-2]]
            vacio = [None] * self.ancho
            self.grid = [vacio[:], vacio[:]] + nuevo_grid
            for _ in range(2):
                self.ejecutar_evento('ON_LINE_CLEAR')   
            self.poderes_tetris.remove("tsunami")

#Método usado para el poder de Bomba
    def tetris_aplicar_gravedad_a_matriz(self, fila_inicio):
        for x in range(self.ancho):
            columna_bloques = []
            for y in range(self.alto):
                if self.grid[y][x] is not None:
                    columna_bloques.append(self.grid[y][x])
            # Volver a llenar la columna desde abajo
            for y in range(self.alto - 1, -1, -1):
                if columna_bloques:
                    self.grid[y][x] = columna_bloques.pop()
                else:
                    self.grid[y][x] = None
        self.tetris_limpiar_lineas()

    def tetris_bomba(self):
            
            if "bomba" in self.poderes_tetris:
                # Eliminar la pieza actual, si existe
                self.pieza_actual = None 
                # Centro del ancho: self.ancho // 2
                # El -2 es para centrar el bloque 5x5 en el ancho
                x_bomba_inicio = self.ancho // 2 - 2
                y_bomba_inicio = self.alto - 5
                
                for y_offset in range(5): # Iterar 5 filas
                    for x_offset in range(5): # Iterar 5 columnas
                        # Calcular la posición absoluta en la cuadrícula
                        current_y = y_bomba_inicio + y_offset
                        current_x = x_bomba_inicio + x_offset
                        
                        # Verificar límites para evitar errores (especialmente si x_bomba_inicio o y_bomba_inicio ajustaron)
                        if 0 <= current_y < self.alto and 0 <= current_x < self.ancho:
                            self.grid[current_y][current_x] = 0 # Limpia la celda
                
                # Aplicar gravedad a las piezas por encima del área limpiada
                self.tetris_aplicar_gravedad_a_matriz(y_bomba_inicio)
                
                # Eliminar el poder de la lista
                self.poderes_tetris.remove("bomba")

                # Generar una nueva pieza para reanudar el juego 
                self.ejecutar_evento('ON_START')

    def funcion_modo_espejo(self):
        if not self.modo_espejo:
            if self.tipo_juego == "Tetris":
                if random.random() < self.probabilidad_espejo:
                    self.modo_espejo = True
                    #Establecemos el tiempo de finalización
                    self.tiempo_fin_espejo = time.time() + 10.0
            else:
                self.modo_espejo = True
                #Establecemos el tiempo de finalización
                self.tiempo_fin_espejo = time.time() + 10.0

    def generar_poderes_tetris(self):
        if len(self.poderes_tetris) < 2:
            if random.random() < self.probabilidad_poderes:
                if "tsunami" in self.poderes_tetris:
                    self.poderes_tetris.append("bomba")
                elif "bomba" in self.poderes_tetris:
                    self.poderes_tetris.append("tsunami")
                else: 
                    opcion = random.choice(["tsunami", "bomba"])
                    self.poderes_tetris.append(opcion)
            else:
                return
    
    def snake_spawn_jugador(self, accion):
        coords = accion['params'][0] if accion['params'] else [self.ancho / 2, self.alto / 2]
        self.serpiente_cuerpo = [(coords[0], coords[1])]
        self.serpiente_direccion = (1, 0)
        
    def snake_spawn_comida(self):
        while True:
            x, y = random.randint(0, self.ancho - 1), random.randint(0, self.alto - 1)
            if (x, y) not in self.serpiente_cuerpo:
                frutas_disponibles = ["@@", "??", "&&", "!!"] #@@ = manzana, ?? = borojo, && = chontaduro, !! = fruta venenosa
                fruta_aleatoria = random.choice(frutas_disponibles)
                self.fruta_actual = fruta_aleatoria
                self.posicion_comida = (x, y)
                break
    
    def snake_mover_jugador(self):
        if not self.serpiente_cuerpo: return
        cabeza_x, cabeza_y = self.serpiente_cuerpo[0]
        dir_x, dir_y = self.serpiente_direccion
        nueva_cabeza = (cabeza_x + dir_x, cabeza_y + dir_y)

        if not (0 <= nueva_cabeza[0] < self.ancho and 0 <= nueva_cabeza[1] < self.alto):
            self.ejecutar_evento('ON_COLLISION_WALL')
            return
            
        if nueva_cabeza in self.serpiente_cuerpo[:-1]:
            self.ejecutar_evento('ON_COLLISION_SELF')
            return

        self.serpiente_cuerpo.insert(0, nueva_cabeza)
        
        if nueva_cabeza == self.posicion_comida:
            if self.fruta_actual == "@@": # Fruta manzana
                self.ejecutar_evento('ON_EAT_FOOD')
            
            elif self.fruta_actual == "??": # Borojo
                self.funcion_modo_espejo()
                self.ejecutar_evento('ON_EAT_FOOD') # Hacemos aparecer nuevamente una fruta y aumentamos el tamaño de la serpiente
            
            elif self.fruta_actual == "&&": # Chontaduro
                self.modo_lento = True
                self.velocidad_gravedad = 0.30 # Lo hacemos más lento
                self.tiempo_fin_lento = time.time() + 10.0
                self.ejecutar_evento('ON_EAT_FOOD') # Hacemos aparecer nuevamente una fruta y aumentamos el tamaño de la serpiente

            elif self.fruta_actual == "!!":
                self.ejecutar_evento('ON_EAT_VENOM')
                self.ejecutar_evento('ON_EAT_FOOD') # Hacemos aparecer nuevamente una fruta
                self.serpiente_cuerpo.pop() # Borramos el crecimiento de la serpiente
        else:
            self.serpiente_cuerpo.pop()

    def snake_cambiar_direccion(self, direccion):
        if direccion == 'UP' and self.serpiente_direccion[1] != 1:
            self.serpiente_direccion = (0, -1)
        elif direccion == 'DOWN' and self.serpiente_direccion[1] != -1:
            self.serpiente_direccion = (0, 1)
        elif direccion == 'LEFT' and self.serpiente_direccion[0] != 1:
            self.serpiente_direccion = (-1, 0)
        elif direccion == 'RIGHT' and self.serpiente_direccion[0] != -1:
            self.serpiente_direccion = (1, 0)

    def snake_crecer(self):
        pass

    def snake_encoger(self):
        if len(self.serpiente_cuerpo) > 4:
            self.serpiente_cuerpo.pop()
        else:
            pass # No hace nada si la serpiente está en su estado inicial

    def mostrar_game_over(self):
        self.canvas.delete("all")
        self.canvas.create_text(self.ancho * self.tamano_celda // 2 + 5,
                                self.alto * self.tamano_celda // 2,
                                text="JUEGO TERMINADO\nPuntuación: {}".format(self.puntuacion),
                                fill="red", font=("Courier", 16, "bold"), justify=tk.CENTER)
        self.root.after(3000, self.salir)  # Cierra después de 3 segundos
    
    def salir(self):
        self.root.quit()
        self.root.destroy()

    def actualizar(self):
        if self.juego_terminado:
            self.mostrar_game_over()
            return
        
        tiempo_actual = time.time()
        delta_tiempo = tiempo_actual - self.ultima_actualizacion
        self.ultima_actualizacion = tiempo_actual

        # Temporizadores
        if self.modo_espejo and tiempo_actual >= self.tiempo_fin_espejo:
            self.modo_espejo = False
            self.tiempo_fin_espejo = 0.0

        if self.tipo_juego == "SNAKE" and self.modo_lento and tiempo_actual >= self.tiempo_fin_lento:
            self.modo_lento = False
            self.tiempo_fin_lento = 0.0
            self.velocidad_gravedad = self.velocidad_base_snake
        
        self.timer_gravedad += delta_tiempo
        if self.timer_gravedad > self.velocidad_gravedad:
            self.timer_gravedad = 0
            self.ejecutar_evento('ON_TICK')
        
        self.dibujar()
        # Programar próxima actualización
        self.root.after(20, self.actualizar)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python runtime.py <archivo_juego.json>")
        sys.exit(1)

    archivo_juego = sys.argv[1]
    try:
        with open(archivo_juego, 'r') as f:
            datos_juego = json.load(f)
    except IOError:
        print("Error: No se pudo encontrar el archivo " + archivo_juego)
        sys.exit(1)

    root = tk.Tk()
    root.title("BrickScript - Juego")
    root.resizable(False, False)
    # Forzar ventana al frente (opcional en XP)
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))

    juego = Juego(datos_juego, root)
    root.mainloop()