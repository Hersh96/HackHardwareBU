import arcade
from constants import ENEMY_HEALTH

class Enemy(arcade.Sprite):
    def __init__(self, image_file, scaling):
        super().__init__(image_file, scaling)
        self.health = ENEMY_HEALTH
        self.shoot_timer = 0  # Shooting cooldown timer

    def update(self):
        super().update()
        # Movement and other behaviors are handled in main.py
