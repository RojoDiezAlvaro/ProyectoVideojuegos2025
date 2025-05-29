"""
Battle View
"""
import arcade
import random
from PIL import Image
import rpg.constants as constants

IMAGE_PATH = "../resources/maps/fotopuz.png"

NUM_COLS = 6
NUM_ROWS = 4

with Image.open(IMAGE_PATH) as img:
    IMAGE_WIDTH, IMAGE_HEIGHT = img.size

TILE_WIDTH = IMAGE_WIDTH // NUM_COLS
TILE_HEIGHT = IMAGE_HEIGHT // NUM_ROWS

SCREEN_WIDTH = TILE_WIDTH * NUM_COLS
SCREEN_HEIGHT = TILE_HEIGHT * NUM_ROWS


class Tile:
    def __init__(self, texture, correct_row, correct_col):
        self.texture = texture
        self.correct_row = correct_row
        self.correct_col = correct_col
        self.current_row = correct_row
        self.current_col = correct_col

    def is_in_correct_position(self):
        return self.current_row == self.correct_row and self.current_col == self.correct_col


class PuzzleView(arcade.View):
    def __init__(self):
        super().__init__()
        self.started = False
        self.tiles = []
        self.selected_tile = None
        self.solved = False  # Bandera de victoria
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        self.tiles = []
        self.selected_tile = None
        self.solved = False  # Reiniciar bandera
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                texture = arcade.load_texture(IMAGE_PATH,
                                              x=col * TILE_WIDTH,
                                              y=row * TILE_HEIGHT,
                                              width=TILE_WIDTH,
                                              height=TILE_HEIGHT)
                tile = Tile(texture, row, col)
                self.tiles.append(tile)

        positions = [(row, col) for row in range(NUM_ROWS) for col in range(NUM_COLS)]
        random.shuffle(positions)
        for tile, (row, col) in zip(self.tiles, positions):
            tile.current_row = row
            tile.current_col = col

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

    def on_draw(self):
        arcade.start_render()

        for tile in self.tiles:
            x = tile.current_col * TILE_WIDTH + TILE_WIDTH // 2
            y = SCREEN_HEIGHT - (tile.current_row * TILE_HEIGHT + TILE_HEIGHT // 2)
            arcade.draw_texture_rectangle(x, y, TILE_WIDTH, TILE_HEIGHT, tile.texture)

            if tile == self.selected_tile:
                arcade.draw_rectangle_outline(x, y, TILE_WIDTH, TILE_HEIGHT, arcade.color.RED, 3)

        if self.solved:
            # una vez resuelto el puzzle, dirigir a mapa de momento solo se dibuja un mensaje
            arcade.draw_text(
                "¡Puzzle resuelto!",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                arcade.color.YELLOW,
                font_size=40,
                anchor_x="center",
                anchor_y="center",
                bold=True,
            )

    def on_mouse_press(self, x, y, button, modifiers):
        if self.solved:
            return  # No permitir más clics si ya fue resuelto

        col = x // TILE_WIDTH
        row = (SCREEN_HEIGHT - y) // TILE_HEIGHT
        clicked_tile = self.get_tile_at(row, col)

        if not clicked_tile:
            return

        if self.selected_tile:
            # Intercambiar posiciones
            clicked_tile.current_row, self.selected_tile.current_row = self.selected_tile.current_row, clicked_tile.current_row
            clicked_tile.current_col, self.selected_tile.current_col = self.selected_tile.current_col, clicked_tile.current_col
            self.selected_tile = None
        else:
            self.selected_tile = clicked_tile

        if self.is_solved():
            self.solved = True  # Activar bandera de victoria

    def get_tile_at(self, row, col):
        for tile in self.tiles:
            if tile.current_row == row and tile.current_col == col:
                return tile
        return None

    def is_solved(self):
        return all(tile.is_in_correct_position() for tile in self.tiles)
