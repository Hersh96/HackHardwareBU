#ammo_pickup.py
import arcade

class AmmoPickup(arcade.SpriteCircle):
    def __init__(self, radius, color, x, y):
        super().__init__(radius, color)
        self.center_x = x
        self.center_y = y

    def update(self):
        super().update()
        # Additional ammo pickup-specific updates can be added here
