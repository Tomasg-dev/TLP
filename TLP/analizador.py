# -*- coding: utf-8 -*-
"""
Created on Sat Sep 26 16:18:17 2025

@author: Tomás Aristizábal Gómez, Andrés Felipe Chica Ospina, Juan Nicolás Chaparro Rodríguez
"""

import json
import re
import os
import sys

class Tokenizer:
    """
    Analizador Lexico (Lexer)
    """
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []

    def tokenize(self):
        lines = self.source.splitlines()
        for line in lines:

            comment_start_index = line.find('//')
            if comment_start_index != -1:
                line = line[:comment_start_index]
                
            line = line.split('//', 1)[0].strip()
            
            if not line or line.startswith('//'):
                continue

            regex_tokens = re.findall(r'(class|int|float|str|list)\s*|"([^"]*)"|(-?\d+\.?\d*)|({|}|\[|\]|=|,)|(\w+)', line)

            for group in regex_tokens:
                if group[0]: 
                    self.tokens.append(('TYPE', group[0]))
                elif group[1]:  # Es una cadena de texto
                    self.tokens.append(('STRING', group[1]))
                elif group[2]:  # Es un numero
                    if '.' in group[2]:
                        self.tokens.append(('NUMBER', float(group[2])))
                    else:
                        self.tokens.append(('NUMBER', int(group[2])))
                elif group[3]:  # Es un operador o delimitador
                    self.tokens.append(('OPERATOR', group[3]))
                elif group[4]:  # Es un identificador
                    self.tokens.append(('IDENTIFIER', group[4]))
                    
        return self.tokens
    

class Parser:
    """
    Analizador Sintactico (Parser)
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.symbol_table = {}

    def parse(self):
        while self.current_token_index < len(self.tokens):
            if self.peek_token() is None:
                break
            
            type_token = self.get_token()  
            if type_token[0] != 'TYPE':
                raise SyntaxError("Error de sintaxis: Se esperaba el tipo del dato, se encontro %s" % type_token[1])
            
            expected_type = type_token[1]
            
            key_token = self.get_token()
            if key_token[0] != 'IDENTIFIER':
                raise SyntaxError("Error de sintaxis: Se esperaba un identificador, se encontro %s" % key_token[1])
            
            eq_token = self.get_token()
            if eq_token[1] != '=':
                raise SyntaxError("Error de sintaxis: Se esperaba '=', se encontro %s" % eq_token[1])
            
            # Obtenemos el tipo y el valor
            value_type, value = self.parse_value()

            # Realizamos la validación de tipos aquí 
            if expected_type == 'float' and value_type == 'int':
                # Permitimos la conversión de int a float (coerción de tipo)
                pass
            elif expected_type != value_type:
                raise TypeError("Error de tipo: Se esperaba '%s' pero se encontró '%s' para el identificador '%s'" % (expected_type, value_type, key_token[1]))

            self.symbol_table[key_token[1]] = value
            # print(self.symbol_table)
        return self.symbol_table

    def get_token(self):
        if self.current_token_index < len(self.tokens):
            token = self.tokens[self.current_token_index]
            self.current_token_index += 1
            return token
        return None

    def peek_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def parse_value(self):

        token = self.peek_token()
        if token is None:
            raise SyntaxError("Error de sintaxis: Se esperaba un valor")

        token_type, token_value = token

        if token_type == 'STRING':
            self.current_token_index += 1
            return ('str', token_value) # Devolvemos el tipo junto con el valor
        
        elif token_type == 'NUMBER':
            self.current_token_index += 1
            val_type = 'float' if isinstance(token_value, float) else 'int'
            return (val_type, token_value) # Devolvemos el tipo junto con el valor

        elif token_type == 'OPERATOR' and token_value == '{':
            return ('class', self.parse_block())

        elif token_type == 'OPERATOR' and token_value == '[':
            return ('list', self.parse_list())

        raise SyntaxError("Error de sintaxis: Valor inesperado '%s'" % token_value)


    def parse_block(self):
        self.get_token() # Consume '{'
        block_content = {}
        
        while self.peek_token() and self.peek_token()[1] != '}':

            type_token = self.get_token()
            if type_token[0] != 'TYPE':
                raise SyntaxError("Error de sintaxis en bloque: Se esperaba un tipo de dato, se encontro %s" % type_token[1])

            key_token = self.get_token()
            if key_token[0] != 'IDENTIFIER':
                raise SyntaxError("Error de sintaxis en bloque: Se esperaba un identificador, se encontro %s" % key_token[1])
            
            eq_token = self.get_token()
            if eq_token[1] != '=':
                raise SyntaxError("Error de sintaxis en bloque: Se esperaba '=', se encontro %s" % eq_token[1])
            
            value_type, value = self.parse_value()
            block_content[key_token[1]] = value

        self.get_token() # Consume '}'
        return block_content
    
    def parse_list(self):
        self.get_token() # Consume '['
        list_content = []
        
        while self.peek_token() and self.peek_token()[1] != ']':
            token_type, token_value = self.peek_token()
            
            if token_type == 'IDENTIFIER':
                # Nuevo: Busca el identificador en la tabla de simbolos
                self.get_token()
                if token_value not in self.symbol_table:
                    raise NameError("Error semantico: El identificador '%s' no ha sido definido." % token_value)
                list_content.append(self.symbol_table[token_value])
            else:
                value_type, item = self.parse_value()
                list_content.append(item)
            
            if self.peek_token() and self.peek_token()[1] == ',':
                self.get_token() # Consume ','
                
        self.get_token() # Consume ']'
        return list_content


def load_file_content(filepath):
    """
    Carga el contenido de un archivo de texto.
    Maneja el error si el archivo no existe.
    """
    if not os.path.exists(filepath):
        print ("Error: El archivo '%s' no se encontro. Asegurate de que el archivo exista en la misma carpeta que el script.") % filepath
        return None
    
    with open(filepath, 'r') as file:
        return file.read()

def save_ast_to_file(ast, filepath):
    """
    Guarda el AST en un archivo de texto en formato JSON.
    """
    try:
        with open(filepath, 'w') as file:
            json.dump(ast, file, indent=4)
        print ("AST guardado exitosamente en '%s'" % filepath)
    except Exception as e:
        print ("Error al guardar el archivo: %s" % e)
        
def transform_ast(symbol_table):
    """
    Transforma la Tabla de Símbolos (AST declarativo) en la estructura JSON
    esperada por el Runtime original (basado en eventos y configuraciones).
    """
    
    # 1. INFERIR TIPO DE JUEGO
    if 'figuras_disponibles' in symbol_table:
        game_type = 'TETRIS'
    elif 'la_cobra' in symbol_table:
        game_type = 'SNAKE'
    else:
        raise Exception("Error: No se pudo inferir el tipo de juego (TETRIS o SNAKE).")

    ast_runtime = {
        "tipo_juego": game_type,
        "config": {},
        "shapes": {}, # Solo usado por TETRIS
        "events": {
            # Eventos generales (necesarios para el Runtime)
            "ON_START": [],
            "ON_TICK": [],
            # Eventos específicos de Tetris
            "ON_LINE_CLEAR": [],
            "ON_TSUNAMI": [],
            # Eventos específicos de Snake
            "ON_EAT_FOOD": [],
            "ON_COLLISION_WALL": [],
            "ON_COLLISION_SELF": [],
            # Eventos de teclado (compartidos, pero las acciones varían)
            "ON_KEY_UP": [],
            "ON_KEY_DOWN": [],
            "ON_KEY_LEFT": [],
            "ON_KEY_RIGHT": [],
        }
    }
    
    # Mapeo de configuraciones (Grid Size)
    if 'dimension' in symbol_table and isinstance(symbol_table['dimension'], list):
        ast_runtime['config']['grid_size'] = symbol_table['dimension']
    elif 'tablero' in symbol_table and isinstance(symbol_table['tablero'], list):
        ast_runtime['config']['grid_size'] = symbol_table['tablero']

    # 2. TRANSFORMACIÓN ESPECÍFICA POR TIPO DE JUEGO
    # ----------------------------------------------------------------------
    
    if game_type == 'TETRIS':
        # **********************************************
        # 2A. Lógica para TETRIS (Reutiliza tu mapeo anterior)
        # **********************************************
        
        # Mapeo de Figuras (SHAPES)
        for key, value in symbol_table.items():
            if key.startswith('figura_') and isinstance(value, dict):
                nombre_pieza = key.upper()
                rotaciones_procesadas = []
                
                if 'rotaciones' in value and isinstance(value['rotaciones'], list):
                    for rotacion in value['rotaciones']:
                        # Lógica para determinar el tamaño de la matriz y convertir coordenadas
                        max_x, max_y = 0, 0
                        for x, y in rotacion:
                            max_x = max(max_x, x)
                            max_y = max(max_y, y)
                        
                        size = max(max_x, max_y) + 1 
                        matriz_bits = [[0 for _ in range(size)] for _ in range(size)]
                        
                        for x, y in rotacion:
                            if y < size and x < size:
                                matriz_bits[y][x] = 1
                        
                        rotaciones_procesadas.append(matriz_bits)

                ast_runtime['shapes'][nombre_pieza] = rotaciones_procesadas

        # Mapeo de Eventos (ON START, ON TICK, ON LINE_CLEAR)
        
        # ON START: SPAWN RANDOM_SHAPE
        ast_runtime['events']['ON_START'].append({'accion': 'SPAWN', 'objeto': 'RANDOM_SHAPE', 'params': []})

        # ON TICK: MOVE CURRENT_PIECE DOWN (Gravedad)
        ast_runtime['events']['ON_TICK'].append({'accion': 'MOVE', 'objeto': 'CURRENT_PIECE', 'params': ['DOWN']})

        # ON LINE_CLEAR: Puntuación (asumiendo que regla_puntuacion se mapea aquí)
        if 'regla_puntuacion' in symbol_table:
             regla_p = symbol_table['regla_puntuacion']
             puntos = regla_p.get('puntos', 10) # 10 es el valor por defecto en tu definición
             ast_runtime['events']['ON_LINE_CLEAR'].append({'accion': 'INCREASE_SCORE', 'objeto': puntos, 'params': []})
             
        # Mapeo de Controles (Movimiento Tetris)
        ast_runtime['events']['ON_KEY_LEFT'].append({'accion': 'MOVE', 'objeto': 'CURRENT_PIECE', 'params': ['LEFT']})
        ast_runtime['events']['ON_KEY_RIGHT'].append({'accion': 'MOVE', 'objeto': 'CURRENT_PIECE', 'params': ['RIGHT']})
        ast_runtime['events']['ON_KEY_DOWN'].append({'accion': 'MOVE', 'objeto': 'CURRENT_PIECE', 'params': ['DOWN']})
        ast_runtime['events']['ON_KEY_UP'].append({'accion': 'ROTATE', 'objeto': 'CURRENT_PIECE', 'params': []})
        
        # Mapeo de Regla Tsunami
        ast_runtime['events']['ON_TSUNAMI'] = [{'accion': 'DESTROY_ROW','objeto': 2, 'params': []}]
        
        # Mapeo de Regla Bomba
        if 'regla_bomba' in symbol_table:
            regla_b = symbol_table['regla_bomba']
            ast_runtime['events']['ON_BOMB'] = [{
                'accion': 'EXPLODE',
                'objeto': None,
                'params': [regla_b.get('radio', 1)]
            }]
        
        # ... (El compilador ignora los controles específicos 't' y 'k',
        #     ya que el Runtime los tiene codificados para disparar los eventos
        #     ON_TSUNAMI y ON_BOMB condicionalmente) ...

    # ----------------------------------------------------------------------
    
    elif game_type == 'SNAKE':
        # **********************************************
        # 2B. Lógica para SNAKE (Nuevo mapeo)
        # **********************************************
        
        # Mapeo de Componentes Iniciales (ON START)
        # Inicializar Jugador (Serpiente) y la primera Comida
        
        cobra = symbol_table.get('la_cobra', {})
        initial_coords = cobra.get('cuerpo', [[10, 10]])[0] # Usa la cabeza como coordenada inicial de spawn
        
        # ON START: SPAWN PLAYER AT (x, y)
        ast_runtime['events']['ON_START'].append({
            'accion': 'SPAWN', 
            'objeto': 'PLAYER', 
            'params': [initial_coords]
        })
        
        # ON START: SPAWN FOOD (Para que el juego empiece con comida)
        ast_runtime['events']['ON_START'].append({
            'accion': 'SPAWN', 
            'objeto': 'FOOD', 
            'params': []
        })

        # Mapeo de Movimiento (ON TICK)
        # El tick controla la velocidad de la serpiente
        # ON TICK: MOVE PLAYER
        ast_runtime['events']['ON_TICK'].append({'accion': 'MOVE', 'objeto': 'PLAYER', 'params': []})

        
        # Mapeo de Reglas de Juego y Colisiones
        
        # Regla de Fin de Juego: Mapeo de Choques a GAME_OVER
        if 'regla_fin_juego' in symbol_table:
            for evento in symbol_table['regla_fin_juego'].get('evento', []):
                if evento == 'choque_pared':
                     ast_runtime['events']['ON_COLLISION_WALL'].append({'accion': 'GAME_OVER', 'objeto': None, 'params': []})
                elif evento == 'choque_cuerpo':
                     ast_runtime['events']['ON_COLLISION_SELF'].append({'accion': 'GAME_OVER', 'objeto': None, 'params': []})

        # Regla de Crecimiento (al comer): ON_EAT_FOOD
        if 'regla_crecimiento' in symbol_table:
            regla_c = symbol_table['regla_crecimiento']
            if regla_c.get('evento') == 'crecimiento_serpiente':
                # Al comer, la serpiente crece y se genera nueva comida
                ast_runtime['events']['ON_EAT_FOOD'].append({'accion': 'GROW', 'objeto': 'PLAYER', 'params': []})
                ast_runtime['events']['ON_EAT_FOOD'].append({'accion': 'SPAWN', 'objeto': 'FOOD', 'params': []})
                
                # Aumentar puntuación
                puntos = regla_c.get('puntos', 1)
                ast_runtime['events']['ON_EAT_FOOD'].append({'accion': 'INCREASE_SCORE', 'objeto': puntos, 'params': []})
                
        pass 
        
    return ast_runtime

# --- Zona de ejecucion ---
# 1. Especifica la ruta del archivo a procesar
file_path = "games\Tetris.brik"
ast_file_path = file_path.replace('.brik', '.json')

# 2. Carga el contenido del archivo
source_code = load_file_content(file_path)

if source_code:
    # 3. Analisis Lexico
    print ("--- Analisis Lexico (Lexer) ---")
    tokenizer = Tokenizer(source_code)
    tokens = tokenizer.tokenize()
    print ("Tokens reconocidos: (%d tokens)" % len(tokens))
    
    # 4. Analisis Sintactico y gestion de Tabla de Simbolos
    print ("\n--- Analisis Sintactico (Parser) ---")
    parser = Parser(tokens)
    try:
        # Aquí se obtiene el AST en formato de Tabla de Símbolos
        symbol_table = parser.parse() 
        print( "Sintaxis correcta. Se ha construido la Tabla de Simbolos.")
        
        # 5. Transformación del AST a formato Runtime
        print ("\n--- Transformación de AST a formato Runtime ---")
        ast_runtime = transform_ast(symbol_table)
        print ("Transformación exitosa. Mapeo a la estructura del motor de juego (runtime).")
        
        # 6. Guardar el AST de Runtime en el archivo JSON
        save_ast_to_file(ast_runtime, ast_file_path)
        print ("\nCompilación finalizada con éxito. Archivo de juego creado en '%s'" % ast_file_path)
        
    except (SyntaxError, NameError, TypeError) as e:
        print ("\n!!! ERROR EN EL PROCESO DE COMPILACIÓN !!!")
        print ("Error: %s" % e)
        sys.exit(1)
