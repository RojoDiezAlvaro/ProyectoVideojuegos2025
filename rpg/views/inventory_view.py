import arcade
import arcade.gui
from arcade.gui import UIFlatButton

# Constantes
COLUMNAS = 9
FILAS = 3
TAM_SLOT = 64
ESPACIADO = 10

# Clase para un slot del inventario
class Slot:
    def __init__(self, item=None):
        self.item = item

# Clase para un ítem
class Item:
    def __init__(self, nombre, textura_path=None):
        self.nombre = nombre

# Vista del inventario
class InventoryView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.botones_slots = []
        self.slots = [[Slot() for _ in range(COLUMNAS)] for _ in range(FILAS)]
        self.slot_coords = []

    def setup(self):
        self.botones_slots.clear()
        self.slots = [[Slot() for _ in range(COLUMNAS)] for _ in range(FILAS)]
        self.slot_coords.clear()
        self.crear_slots()

    def crear_slots(self):
        pantalla_ancho, pantalla_alto = self.window.width, self.window.height
        total_ancho = COLUMNAS * TAM_SLOT + (COLUMNAS - 1) * ESPACIADO
        total_alto = FILAS * TAM_SLOT + (FILAS - 1) * ESPACIADO

        base_x = (pantalla_ancho - total_ancho) // 2
        base_y = (pantalla_alto - total_alto) // 2

        for fila in range(FILAS):
            fila_botones = []
            for col in range(COLUMNAS):
                x = base_x + col * (TAM_SLOT + ESPACIADO)
                y = base_y + fila * (TAM_SLOT + ESPACIADO)

                texto = self.slots[fila][col].item or ""

                btn = UIFlatButton(
                    text=texto,
                    width=TAM_SLOT,
                    height=TAM_SLOT
                )

                btn.fila = fila
                btn.col = col

                @btn.event("on_click")
                def al_click(event, btn=btn):
                    slot = self.slots[btn.fila][btn.col]
                    if slot.item:
                        print(f"Slot ({btn.fila},{btn.col}) contiene: {slot.item.nombre}")
                    else:
                        print(f"Slot ({btn.fila},{btn.col}) está vacío.")

                self.manager.add(arcade.gui.UIAnchorWidget(
                    anchor_x="left",
                    anchor_y="bottom",
                    align_x=x,
                    align_y=y,
                    child=btn
                ))

                self.slot_coords.append((x, y))  # Coordenada añadida
                fila_botones.append(btn)
            self.botones_slots.append(fila_botones)

    def agregar_item_a_inventario(self, item):
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                if self.slots[fila][col].item is None:
                    self.slots[fila][col].item = item
                    print(f"Agregado {item.nombre} a slot ({fila}, {col})")
                    return
        print("Inventario lleno")

    def on_show(self):
        arcade.set_background_color(arcade.color.ANTIQUE_BRASS)
        self.setup()

    def on_draw(self):
        self.clear()
        arcade.draw_text("INVENTORY",
                         self.window.width // 2,
                         self.window.height - 70,
                         arcade.color.ANTIQUE_RUBY,
                         48,
                         anchor_x="center")
        self.manager.draw()

        for fila in range(FILAS):
            for col in range(COLUMNAS):
                slot = self.slots[fila][col]
                if slot.item:
                    x, y = self.slot_coords[fila * COLUMNAS + col]
                    arcade.draw_texture_rectangle(
                        x + TAM_SLOT / 2,
                        y + TAM_SLOT / 2,
                        TAM_SLOT - 8,
                        TAM_SLOT - 8,
                        slot.item.texture
                    )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.I:
            self.window.show_view(self.window.views["game"])

    def onn_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.E and self.objeto_en_mapa_vivo:
            self.agregar_item_a_inventario(self.objeto_en_mapa)
            self.objeto_en_mapa_vivo = False
