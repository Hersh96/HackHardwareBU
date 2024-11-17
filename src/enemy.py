import arcade
from constants import ENEMY_HEALTH

class Enemy(arcade.Sprite):
    def __init__(self, standing_image, walking_image1, walking_image2, scaling):
        super().__init__(standing_image, scaling)
        self.standing_texture = arcade.load_texture(standing_image)
        self.walking_textures = [
            arcade.load_texture(walking_image1),
            arcade.load_texture(walking_image2),
        ]
        self.current_frame = 0  # For alternating between walking textures
        self.health = ENEMY_HEALTH
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

    def handle_collision(self, wall_list):
        """
        Handle collision with walls and prevent enemies from walking through them.
        """
        # Check for collisions with walls
        walls_hit = arcade.check_for_collision_with_list(self, wall_list)
        for wall in walls_hit:
            # Push the enemy out of the wall
            if self.change_x > 0:  # Moving right
                self.right = wall.left
            elif self.change_x < 0:  # Moving left
                self.left = wall.right
            if self.change_y > 0:  # Moving up
                self.top = wall.bottom
            elif self.change_y < 0:  # Moving down
                self.bottom = wall.top

        # Reset movement to prevent clipping
        if walls_hit:
            self.change_x = 0
            self.change_y = 0
