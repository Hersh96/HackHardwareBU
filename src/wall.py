#wall.py
import arcade

class Wall(arcade.SpriteSolidColor):
    def __init__(self, width, height, color, x, y):
        super().__init__(width, height, color)
        self.center_x = x
        self.center_y = y
