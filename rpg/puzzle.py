import arcade
import json
import base64
import zlib
import array

# --- Configuraciones del Puzzle ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Rompecabezas Deslizante"

TILE_SIZE = 64  # Tamaño de cada pieza grande (casilla)
SUBTILE_SIZE = 8  # Tamaño de cada "mini-tile" dentro de la pieza
GRID_ROWS = 6
GRID_COLS = 6

JSON_FILE = "./resources/maps/puzzle.json"
TILESET_IMAGE = "./resources/tilesets/[Base]BaseChip_pipo.png"
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
        # Cargar tileset
        self.tileset = arcade.load_texture(TILESET_IMAGE)
        self.prepare_tiles()

        # Cargar archivo JSON
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)

        # Solo tomar las capas que son cuadradoX
        layers = [layer for layer in data['layers'] if layer['name'].startswith('cuadrado')]

        # Ordenarlas por su nombre (opcional, por si no vienen ordenadas)
        layers.sort(key=lambda l: int(''.join(filter(str.isdigit, l['name']))))

        # Crear sprites para cada pieza
        for index, layer in enumerate(layers):
            number = int(''.join(filter(str.isdigit, layer['name'])))

            if number == 36:
                # Es el espacio vacío
                self.pieces.append(None)
                continue

            # Decodificar el data
            compressed_data = base64.b64decode(layer['data'])
            decompressed_data = zlib.decompress(compressed_data)
            tile_array = array.array('I')  # Unsigned int 32 bits
            tile_array.frombytes(decompressed_data)

            # Crear una texture para cada pieza
            texture = arcade.Texture.create_empty(f"piece_{number}", (TILE_SIZE, TILE_SIZE))
            image = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.TRANSPARENT, outer_alpha=0)

            # Dibujar los mini-tiles dentro de la imagen
            for row in range(0, TILE_SIZE // SUBTILE_SIZE):
                for col in range(0, TILE_SIZE // SUBTILE_SIZE):
                    idx = row * 48 + col  # 48 es el width total del mapa
                    if idx < len(tile_array):
                        tile_value = tile_array[idx]
                        if tile_value > 0:
                            tile_texture = self.get_tile_texture(tile_value - 1)
                            x = col * SUBTILE_SIZE
                            y = TILE_SIZE - (row + 1) * SUBTILE_SIZE
                            arcade.draw_texture_rectangle(x + SUBTILE_SIZE / 2, y + SUBTILE_SIZE / 2, SUBTILE_SIZE, SUBTILE_SIZE, tile_texture, image)

            # Crear el sprite
            sprite = arcade.Sprite()
            sprite.texture = texture
            sprite.append_texture(texture)
            sprite.set_texture(0)

            self.pieces.append(sprite)

        # Crear el grid y colocar las piezas
        self.grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        piece_idx = 0
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if piece_idx < len(self.pieces):
                    piece = self.pieces[piece_idx]
                    self.grid[row][col] = piece
                    if piece:
                        piece.center_x = col * TILE_SIZE + TILE_SIZE // 2
                        piece.center_y = SCREEN_HEIGHT - (row * TILE_SIZE + TILE_SIZE // 2)
                    else:
                        self.empty_position = (row, col)
                    piece_idx += 1

    def prepare_tiles(self):
        columns = self.tileset.width // TILE_WIDTH
        rows = self.tileset.height // TILE_HEIGHT

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

        # Dibujar todas las piezas
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                piece = self.grid[row][col]
                if piece:
                    piece.draw()

    def on_update(self, delta_time):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        # Luego aquí pondremos lógica para mover piezas
        pass

if __name__ == "__main__":
    window = PuzzleGame()
    window.setup()
    arcade.run()
