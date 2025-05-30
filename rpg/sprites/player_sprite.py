import arcade

from rpg import constants
from rpg.constants import STARTING_Y, STARTING_X, SPRITE_SIZE
from rpg.sprites.character_sprite import CharacterSprite, Direction, SPRITE_INFO

class PlayerSprite(CharacterSprite):
    def __init__(self, sheet_name):
        super().__init__(sheet_name)
        self.sound_update = 0
        self.footstep_sound = arcade.load_sound(":sounds:sonidosPasos .wav")
        self.corpse_sprite = arcade.Sprite("../resources/characters/MainCharacterAndCorpse/CorpseNotFinal.png")
        self.corpse_exists = False
        self.is_ghost = False
        self.starter_checkpoint_x = STARTING_X
        self.starter_checkpoint_y = STARTING_Y
        self.last_checkpoint_x = None
        self.last_checkpoint_y = None
        self.last_checkpoint_map = None
        self.current_map = constants.STARTING_MAP
        #fantasma
        self.ghost_textures = arcade.load_spritesheet(
            "../resources/characters/MainCharacterAndCorpse/Fantasma.png",
            sprite_width=SPRITE_SIZE,
            sprite_height=SPRITE_SIZE,
            columns=3,
            count=12
        )

    def on_update(self, delta_time):
        if self.is_ghost:
            # Evitar animar si no se mueve
            if not self.change_x and not self.change_y:
                return

            # Manejar animación del fantasma
            self.should_update = (self.should_update + 1) % 4
            if self.should_update != 0:
                return

            self.cur_texture_index += 1

            # Determinar dirección
            direction = Direction.LEFT
            slope = self.change_y / (self.change_x + 0.0001)
            if abs(slope) < 0.8:
                direction = Direction.RIGHT if self.change_x > 0 else Direction.LEFT
            else:
                direction = Direction.UP if self.change_y > 0 else Direction.DOWN

            if self.cur_texture_index not in SPRITE_INFO[direction]:
                self.cur_texture_index = SPRITE_INFO[direction][0]

            # Aplicar textura de fantasma
            self.texture = self.ghost_textures[self.cur_texture_index]

            # Comprobar interacción con el cadáver
            self.interact_with_corpse()
            return

        # Si no es fantasma, animación y lógica normal
        super().on_update(delta_time)

        # Actualizar cadáver si existe
        if self.corpse_exists and self.corpse_sprite:
            self.corpse_sprite.update()

    #sistema de checkpoints
    def return_to_checkpoint(self):
        if self.last_checkpoint_x is not None and self.last_checkpoint_y is not None and self.last_checkpoint_map == self.current_map:
            self.center_x = self.last_checkpoint_x
            self.center_y = self.last_checkpoint_y
            print(f"Volviendo al checkpoint: {self.last_checkpoint_x}, {self.last_checkpoint_y}")
            self.change_x = 0
            self.change_y = 0

        else:
            self.center_x = self.starter_checkpoint_x
            self.center_y = self.starter_checkpoint_y
            print(f"Volviendo al inicio: {self.starter_checkpoint_x}, {self.starter_checkpoint_y}, {self.current_map}")
            self.change_x = 0
            self.change_y = 0


    #codigo añadido sin probar(exluyendo las declaraciones en el innit)-----------------------
    #código relacionado a la muerte y el "modo fantasma"
    def is_ghost_function(self):
        return self.is_ghost


    def player_death(self):
        self.spawn_corpse_at(self.center_x, self.center_y)
        self.return_to_checkpoint()
        self.is_ghost = True
        self.cur_texture_index = 0
        self.texture = self.ghost_textures[self.cur_texture_index]


    def spawn_corpse_at(self, x, y):
        # Crear sprite del cadáver
        self.corpse_sprite = arcade.Sprite(
            "../resources/characters/MainCharacterAndCorpse/CorpseNotFinal.png",
            center_x=x,
            center_y=y
        )
        # Hacer que sea visible e interactuable (si lo necesitas)
        self.corpse_sprite.visible = True
        self.corpse_exists = True




    def interact_with_corpse(self):
        if self.corpse_exists and self.corpse_sprite is not None:
            if arcade.check_for_collision(self, self.corpse_sprite):
                print("Colisión con cadáver detectada")  # DEBUG
                # Eliminar cadáver
                self.corpse_sprite = None
                self.corpse_exists = False
                # Restaurar estado
                self.is_ghost = False
                self.cur_texture_index = 0
                self.texture = self.textures[self.cur_texture_index]