import arcade
import json
import base64
import zlib
import array
import os

# --- Configuraciones del Puzzle ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Rompecabezas Deslizante"

TILE_SIZE = 64  # Tamaño de cada pieza grande (casilla)
SUBTILE_SIZE = 8  # Tamaño de cada "mini-tile" dentro de la pieza
GRID_ROWS = 6
GRID_COLS = 6

JSON_FILE = "../resources/maps/puzzle.json"
TILESET_IMAGE = "../resources/tilesets/[Base]BaseChip_pipo.png"
TILE_WIDTH = 32
TILE_HEIGHT = 32

class PuzzleGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.ALMOND)

        self.pieces = []
        self.grid = []
        self.empty_position = (0, 0)

        self.tileset = None
        self.tile_list = []

    def setup(self):
        # Imprimir el directorio de trabajo actual
        print(f"Directorio de trabajo actual: {os.getcwd()}")

        # Cargar tileset
        try:
            self.tileset = arcade.load_texture(TILESET_IMAGE)
        except FileNotFoundError as e:
            print(f"Error al cargar el tileset: {e}")
            arcade.exit()
            return

        self.prepare_tiles()

        # Cargar archivo JSON
        try:
            with open(JSON_FILE, 'r') as f:
                data = json.load(f)
        except FileNotFoundError as e:
            print(f"Error al cargar el archivo JSON: {e}")
            arcade.exit()
            return

        # Solo tomar las capas que son cuadradoX y ordenarlas
        layers = sorted([layer for layer in data['layers'] if layer['name'].startswith('cuadrado')],
                          key=lambda l: int(''.join(filter(str.isdigit, l['name']))))
        print(f"Número de capas encontradas: {len(layers)}") # ADDED
        print(f"Nombres de las capas encontradas: {[layer['name'] for layer in layers]}") # ADDED

        # Crear sprites para cada pieza
        self.pieces = [None] * (GRID_ROWS * GRID_COLS)  # Inicializar la lista de piezas
        piece_index = 0
        subtiles_per_row = TILE_SIZE // SUBTILE_SIZE
        for layer in layers:
            number = int(''.join(filter(str.isdigit, layer['name'])))
            grid_row = (number - 1) // GRID_COLS  # Calcular la fila en la cuadrícula (0-indexed)
            grid_col = (number - 1) % GRID_COLS   # Calcular la columna en la cuadrícula (0-indexed)

            if number == 36:
                # Es el espacio vacío
                self.empty_position = (grid_row, grid_col)
                continue

            # Decodificar el data
            try:
                compressed_data = base64.b64decode(layer['data'])
                decompressed_data = zlib.decompress(compressed_data)
                tile_array = array.array('I')  # Unsigned int 32 bits
                tile_array.frombytes(decompressed_data)
            except Exception as e:
                print(f"Error al decodificar datos de la capa {layer['name']}: {e}")
                continue

            # Crear una texture para cada pieza
            texture = arcade.Texture.create_empty(f"piece_{number}", (TILE_SIZE, TILE_SIZE))
            image = texture.image

            # Dibujar los mini-tiles dentro de la imagen de la pieza
            for row in range(subtiles_per_row):  # Iterar sobre las filas de mini-tiles (0-7)
                for col in range(subtiles_per_row):  # Iterar sobre las columnas de mini-tiles (0-7)
                    tile_index_in_data = row * subtiles_per_row + col  # Cálculo corregido del índice
                    if tile_index_in_data < len(tile_array):
                        tile_value = tile_array[tile_index_in_data]
                        if tile_value > 0:
                            tile_texture = self.get_tile_texture(tile_value - 1)
                            if tile_texture:
                                x_dest = col * SUBTILE_SIZE
                                y_dest = row * SUBTILE_SIZE
                                image.paste(tile_texture.image, (x_dest, TILE_SIZE - SUBTILE_SIZE - y_dest)) # Invertir Y para Arcade
                            else:
                                print(f"Capa: {layer['name']}, tile_value: {tile_value}, tile_texture is None!")
                    # No necesitamos un 'else' aquí
                #else:
                    #print(f"Capa: {layer['name']}, tile_index_in_data out of bounds: {tile_index_in_data}") #REMOVED

            # Crear el sprite
            sprite = arcade.Sprite()
            sprite.texture = texture
            sprite.append_texture(texture)
            sprite.set_texture(0)

            # Calcular la posición del sprite en la pantalla
            center_x = grid_col * TILE_SIZE + TILE_SIZE // 2
            center_y = SCREEN_HEIGHT - (grid_row * TILE_SIZE + TILE_SIZE // 2)
            sprite.center_x = center_x
            sprite.center_y = center_y
            self.pieces[piece_index] = sprite
            piece_index += 1

        # Crear el grid y colocar las piezas (ahora las piezas ya tienen su posición)
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        piece_idx = 0
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if piece_idx < len(self.pieces):
                    self.grid[row][col] = self.pieces[piece_idx]
                    piece_idx += 1

    def prepare_tiles(self):
        columns = self.tileset.width // TILE_WIDTH
        rows = self.tileset.height // TILE_HEIGHT
        self.tile_list = []
        for row in range(rows):
            for col in range(columns):
                x = col * TILE_WIDTH
                y = self.tileset.height - (row + 1) * TILE_HEIGHT
                tile = arcade.load_texture(TILESET_IMAGE, x, y, TILE_WIDTH, TILE_HEIGHT)
                self.tile_list.append(tile)

    def get_tile_texture(self, tile_index):
        if 0 <= tile_index < len(self.tile_list):
            return self.tile_list[tile_index]
        else:
            return None

    def on_draw(self):
        arcade.start_render()
        for piece in self.pieces:
            if piece and piece.texture:
                piece.draw()

    def on_update(self, delta_time):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        grid_x = int(x // TILE_SIZE)
        grid_y = int((SCREEN_HEIGHT - y) // TILE_SIZE)

        if 0 <= grid_y < GRID_ROWS and 0 <= grid_x < GRID_COLS:
            clicked_piece = self.grid[grid_y][grid_x]
            if clicked_piece:
                # Comprobar si la pieza clicada está adyacente al espacio vacío
                empty_y, empty_x = self.empty_position
                if (abs(grid_y - empty_y) == 1 and grid_x == empty_x) or \
                   (abs(grid_x - empty_x) == 1 and grid_y == empty_y):
                    # Intercambiar la pieza clicada con el espacio vacío en la cuadrícula
                    self.grid[empty_y][empty_x] = clicked_piece
                    self.grid[grid_y][grid_x] = None

                    # Actualizar la posición del sprite de la pieza clicada
                    clicked_piece.center_x = empty_x * TILE_SIZE + TILE_SIZE // 2
                    clicked_piece.center_y = SCREEN_HEIGHT - (empty_y * TILE_SIZE + TILE_SIZE // 2)

                    # Actualizar la posición del espacio vacío
                    self.empty_position = (grid_y, grid_x)

def main():
    window = PuzzleGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()