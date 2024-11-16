# enemy.py

import arcade

class Enemy(arcade.Sprite):
    def __init__(self, image_file, scale):
        super().__init__(image_file, scale)

        # Enemy attributes
        self.health = 0
        self.shoot_timer = 0
        self.time_since_last_fire = 0  # Time since the enemy last fired (in frames)

    def update(self):
        # Call parent class update
        super().update()
        # Additional update logic if needed
