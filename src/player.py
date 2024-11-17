#player.py
import arcade
from constants import PLAYER_HEALTH, INITIAL_AMMO

class Player(arcade.Sprite):
    def __init__(self, standing_image, walking_image1, walking_image2, scaling):
        super().__init__(standing_image, scaling)
        self.standing_texture = arcade.load_texture(standing_image)
        self.walking_textures = [
            arcade.load_texture(walking_image1),
            arcade.load_texture(walking_image2),
        ]
        self.dead_texture = arcade.load_texture("Images/dead_sprite_optimized.png")
        smaller_hit_box = [
            (-self.width * 0.85, -self.height * 0.85),  # Bottom-left
            (self.width * 0.85, -self.height * 0.85),  # Bottom-right
            (self.width * 0.8, self.height * 0.8),  # Top-right
            (-self.width * 0.8, self.height * 0.8)  # Top-left
        ]

        self.set_hit_box(smaller_hit_box)
        self.current_frame = 0  # For alternating between walking textures
        self.health = PLAYER_HEALTH
        self.ammo = INITIAL_AMMO
        self.shoot_timer = 0
        self.frame_count = 0  # Counter to control animation speed

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
