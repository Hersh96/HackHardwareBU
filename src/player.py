import arcade
from constants import PLAYER_HEALTH, INITIAL_AMMO

class Player(arcade.Sprite):
    def __init__(self, image_file, scaling):
        super().__init__(image_file, scaling)
        self.health = PLAYER_HEALTH
        self.ammo = INITIAL_AMMO
        self.shoot_timer = 0

    def update(self):
        super().update()
        # Movement and other behaviors are handled in main.py
