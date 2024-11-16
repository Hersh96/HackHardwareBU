import arcade

class Bullet(arcade.SpriteCircle):
    def __init__(self, radius, color, owner, speed):
        super().__init__(radius, color)
        self.owner = owner  # 'player' or 'enemy'
        self.speed = speed

    def update(self):
        super().update()
        # Additional bullet-specific updates can be added here
