"""
Battle View
"""

import arcade
import rpg.constants as constants
class BattleView(arcade.View):
    def __init__(self, previous_view, player_x, player_y):
        super().__init__()
        self.previous_view = previous_view  # Vista anterior (mundo, mapa, etc.)
        self.return_x = player_x
        self.return_y = player_y

        super().__init__()
        self.started = False
        self.background_1 = None
        self.background_2 = None
        self.current_background = None
        arcade.set_background_color(arcade.color.BLUE)
        # Lista de botones con sus posiciones, etiquetas y teclas asociadas
        self.buttons = []
        self.player_hp = 100
        self.enemy_hp = 20
        self.message = "¿Qué vas a hacer?"
        self.message_timer = 0
        self.full_message = ""  # Mensaje completo
        self.displayed_message = ""  # Lo que se muestra letra a letra
        self.message_speed = 40  # Letras por segundo
        self.message_char_index = 0  # Índice actual de la letra
        self.state = "player_turn"  # Otros: "enemy_wait", "enemy_attack"
        self.enemy_timer = 0
        self.player_texture = None
        self.player_frame = None
        self.enemy_sprite = None

        self.player_pos = [300, 250]  # Posición base del jugador
        self.enemy_pos = [900, 250]  # Posición base del enemigo

        self.attack_animation = False
        self.attack_timer = 0
        self.attacker = None  # "player" o "enemy"

    def setup(self):
        self.background_1 = arcade.load_texture("../resources/maps/cavernaBattleScreen.png")
        self.background_2 = arcade.load_texture("../resources/maps/desiertoBattleScreen.png")
        self.current_background = self.background_1
        self.enemy_sprite = arcade.load_texture("../resources/characters/Enemy/Armadura_viviente.png")
        self.player_texture = arcade.load_spritesheet(
            "../resources/characters/MainCharacterAndCorpse/PlayerCombat.png",  # ruta de tu spritesheet
            sprite_width=145,
            sprite_height=151,
            columns=3,
            count=12
        )
        self.player_frame = self.player_texture[0]  # Frame específico: fila 3, columna 2 (índice 10)


        # Definir los botones con su posición, etiqueta y tecla asociada
        self.buttons = [
            {"label": "ATTACK [A]", "x": self.window.width / 4, "y": 150, "key": arcade.key.A},
            {"label": "ITEMS [I]", "x": 3 * self.window.width / 4, "y": 150, "key": arcade.key.I},
            {"label": "MAGIC [M]", "x": self.window.width / 4, "y": 80, "key": arcade.key.M},
            {"label": "FLEE [F]", "x": 3 * self.window.width / 4, "y": 80, "key": arcade.key.F},
        ]



    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLUE)
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def set_message(self, text: str, duration: float = 2.0):
        self.full_message = text
        self.displayed_message = ""
        self.message_char_index = 0
        self.message_timer = duration

    def player_attack(self):
        damage = 10
        self.enemy_hp -= damage
        if self.enemy_hp <= 0:
            self.enemy_hp = 0
            self.set_message("¡Enemigo derrotado!", 2)
            self.state = "battle_won"
        else:
            self.set_message(f"¡Atacaste! El enemigo ha perdido {damage} HP.", 2)
            self.state = "enemy_wait"
            self.enemy_timer = 1.0  # Espera 1 segundo antes de "Turno enemigo"
        # Animación del jugador atacando
        self.attack_animation = True
        self.attack_timer = 0.3  # duración total del golpe
        self.attacker = "player"

    def enemy_turn(self):
        damage = 8
        self.player_hp -= damage
        if self.player_hp <= 0:
            self.player_hp = 0
            self.set_message("Has muerto...", 3)
        else:
            self.set_message(f"¡Te atacan! Has perdido {damage} HP.", 2)
        # Animación del enemigo atacando
        self.attack_animation = True
        self.attack_timer = 0.3
        self.attacker = "enemy"

    def draw_button(self, x, y, width, height, text):
        """Dibuja un botón rectangular con texto centrado"""
        arcade.draw_rectangle_filled(x, y, width, height, arcade.color.DARK_BLUE_GRAY)
        arcade.draw_rectangle_outline(x, y, width, height, arcade.color.WHITE, 2)
        arcade.draw_text(
            text, x, y,
            arcade.color.WHITE, 18,
            anchor_x="center", anchor_y="center"
        )

    def on_draw(self):#makes text apear on screen. The blue background will not draw w/o this
        arcade.start_render()
        if self.current_background:
            arcade.draw_lrwh_rectangle_textured(
                0, 0, self.window.width, self.window.height, self.current_background
            )

        if self.player_frame:
            arcade.draw_texture_rectangle(
                self.player_pos[0], self.player_pos[1],
                64, 64,  # Puedes ajustar el tamaño si lo ves muy pequeño o grande
                self.player_frame
            )

        if self.enemy_sprite:
            arcade.draw_texture_rectangle(self.enemy_pos[0], self.enemy_pos[1],
                                          self.enemy_sprite.width, self.enemy_sprite.height,
                                          self.enemy_sprite)

        # Título superior
        arcade.draw_text(
            "BATTLE",
            self.window.width / 2,
            self.window.height - 50,
            arcade.color.WHITE,
            44,
            anchor_x="center",
            anchor_y="center",
        )
        # Mostrar HP del jugador y enemigo
        arcade.draw_text(f"Player HP: {self.player_hp}", 50, self.window.height - 100,
                         arcade.color.WHITE, 20)
        arcade.draw_text(f"Enemy HP: {self.enemy_hp}", self.window.width - 200,
                         self.window.height - 100, arcade.color.WHITE, 20)

        # Mostrar mensaje de combate
        arcade.draw_text(self.displayed_message, self.window.width / 2, self.window.height / 4,
                         arcade.color.LIGHT_GOLDENROD_YELLOW, 20, anchor_x="center",
                         align="center", width=self.window.width - 100)

        # Dibuja todos los botones desde la lista
        for button in self.buttons:
            self.draw_button(button["x"], button["y"], 200, 50, button["label"])

    def on_key_press(self, symbol: int, modifiers: int):
        if self.state != "player_turn":
            return  # Ignora pulsaciones si no es el turno del jugador

        if symbol == arcade.key.ESCAPE:
            self.window.show_view(self.window.views["main_menu"])
        # Buscar el botón cuya tecla coincida y hacer una acción (por ahora solo imprimir)
        for button in self.buttons:
            if symbol == button["key"]:
                if button["label"].startswith("ATTACK"):
                    self.player_attack()
                else:
                    self.message = f"{button['label']} not implemented yet"

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """Detecta clics del ratón y verifica si un botón fue pulsado"""
        if self.state != "player_turn":
            return  # Ignora pulsaciones si no es el turno del jugador
        for btn in self.buttons:
            # Define un área rectangular para cada botón
            half_width = 100
            half_height = 25
            if (btn["x"] - half_width < x < btn["x"] + half_width and
                    btn["y"] - half_height < y < btn["y"] + half_height):
                if btn["label"].startswith("ATTACK"):
                    self.player_attack()
                else:
                    self.message = f"{btn['label']} not implemented yet"

    def on_update(self, delta_time: float):
        # Efecto de texto
        if self.message_char_index < len(self.full_message):
            self.message_char_index += self.message_speed * delta_time
            self.displayed_message = self.full_message[:int(self.message_char_index)]
        else:
            if self.message_timer > 0:
                self.message_timer -= delta_time
                if self.message_timer <= 0:
                    if self.state == "enemy_wait":
                        self.set_message("Turno enemigo...", 1)
                        self.state = "enemy_attack"
                        self.enemy_timer = 1.0
                    elif self.state == "enemy_attack":
                        self.enemy_turn()
                        self.state = "player_turn"
                    elif self.state == "battle_won":
                        # Ya se mostró el mensaje "¡Enemigo derrotado!", ahora salimos
                        self.previous_view.player_sprite.center_x = self.return_x
                        self.previous_view.player_sprite.center_y = self.return_y
                        self.window.show_view(self.previous_view)
                    else:
                        self.set_message("¿Qué vas a hacer?", duration=9999)

        # Temporizador para ataques enemigos
        if self.state == "enemy_attack":
            self.enemy_timer -= delta_time
            if self.enemy_timer <= 0:
                self.enemy_turn()
                self.state = "player_turn"

        # Animación de ataque (desplazamiento)
        if self.attack_animation:
            self.attack_timer -= delta_time
            shift = 10

            if self.attacker == "player":
                if self.attack_timer > 0.15:
                    self.player_pos[0] += shift  # avanza
                else:
                    self.player_pos[0] -= shift  # retrocede
            elif self.attacker == "enemy":
                if self.attack_timer > 0.15:
                    self.enemy_pos[0] -= shift
                else:
                    self.enemy_pos[0] += shift

            if self.attack_timer <= 0:
                self.attack_animation = False
                self.player_pos = [300, 250]
                self.enemy_pos = [900, 250]
