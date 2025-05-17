import arcade

from rpg.constants import STARTING_Y, STARTING_X
from rpg.sprites.character_sprite import CharacterSprite


class PlayerSprite(CharacterSprite):
    def __init__(self, sheet_name):
        super().__init__(sheet_name)
        self.player_sprite = arcade.Sprite("../resources/characters/MainCharacterAndCorpse/PlayerNotFinal.png")
        self.sound_update = 0
        self.footstep_sound = arcade.load_sound(":sounds:sonidosPasos .wav")
        self.corpse_sprite = arcade.Sprite("../resources/characters/MainCharacterAndCorpse/CorpseNotFinal.png")
        self.corpse_exists = False
        self.is_ghost = False
        self.starter_checkpoint_x = STARTING_X
        self.starter_checkpoint_y = STARTING_Y
        self.last_checkpoint_x = None
        self.last_checkpoint_y = None

    def on_update(self, delta_time):
        super().on_update(delta_time)
        saved_x = self.center_x
        saved_y = self.center_y
        if not self.change_x and not self.change_y:
            self.sound_update = 0
            return

        if self.should_update > 3:
            self.sound_update += 1

        if self.sound_update >= 3:
            arcade.play_sound(self.footstep_sound)
            self.sound_update = 0
        self.interact_with_corpse()

        if self.corpse_exists:
            self.corpse_sprite.update()

        # Revisión de interacción con cadáver
        if self.is_ghost:
            self.player_sprite = arcade.Sprite("../resources/characters/MainCharacterAndCorpse/Fantasma.png")
            self.interact_with_corpse()
            # codigo añadido sin probar(excluyendo las declaraciones en el innit)---------------------------------------------

    #sistema de checkpoints
    def return_to_checkpoint(self):
        if self.last_checkpoint_x is not None and self.last_checkpoint_y is not None:
            self.player_sprite.center_x = self.last_checkpoint_x
            self.player_sprite.center_y = self.last_checkpoint_y
        else:
            self.player_sprite.center_x = self.starter_checkpoint_x
            self.player_sprite.center_y = self.starter_checkpoint_y

    #codigo añadido sin probar(exluyendo las declaraciones en el innit)-----------------------
    #código relacionado a la muerte y el "modo fantasma"
    def is_ghost(self):
        return self.is_ghost


    def player_death(self):
        self.spawn_corpse_at(self.player_sprite.center_x, self.player_sprite.center_y)
        self.return_to_checkpoint()
        self.is_ghost = True
        self.player_sprite = arcade.Sprite("Fantasma.png")

    def spawn_corpse_at(self, x, y):
        # Crear sprite del cadáver
        self.corpse_sprite = arcade.Sprite("../resources/characters/MainCharacterAndCorpse/CorpseNotFinal.png", center_x=x, center_y=y)

        # Hacer que sea visible e interactuable (si lo necesitas)
        self.corpse_sprite.visible = True
        self.corpse_exists = True
        self.draw()

    def interact_with_corpse(self):
        #meter fuera de def en on update
        if self.corpse_exists and self.corpse_sprite is not None:
            if arcade.check_for_collision(self.player_sprite, self.corpse_sprite):
                # Eliminar el cadáver
                self.corpse_sprite = None
                self.corpse_exists = False

                # Restaurar jugador a estado normal
                self.is_ghost = False
                self.player_sprite = arcade.Sprite("../resources/characters/MainCharacterAndCorpse/PlayerNotFinal.png.png")
                self.player_sprite.can_collide = True
