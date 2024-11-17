# boss.py

import arcade
from constants import BOSS_HEALTH

class Boss(arcade.Sprite):
    def __init__(self, standing_image, walking_image1, walking_image2, scaling):
        super().__init__(standing_image, scaling)
        self.standing_texture = arcade.load_texture(standing_image)
        self.walking_textures = [
            arcade.load_texture(walking_image1),
            arcade.load_texture(walking_image2),
        ]
        self.current_frame = 0  # For alternating between walking textures
        self.health = BOSS_HEALTH
        self.shoot_timer = 0
        self.frame_count = 0  # Counter to control animation speed
        self.time_since_last_fire = 0

    def update(self):
        super().update()
        # Update walking animation if moving
        if self.change_x != 0 or self.change_y != 0:
            self.frame_count += 1
            if self.frame_count % 10 == 0:  # Adjust animation speed
                self.current_frame = (self.current_frame + 1) % len(self.walking_textures)
                self.texture = self.walking_textures[self.current_frame]
        else:
            self.texture = self.standing_texture
