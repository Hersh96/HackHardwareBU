import arcade
import random

# Constants for the screen size
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Simple Arcade Game"

# Constants for the player
PLAYER_SPEED = 5
PLAYER_SCALE = 0.3
PLAYER_JUMP_SPEED = 30
GRAVITY = 1

# Constants for the ground
GROUND_HEIGHT = 200

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        # Initialize lists to hold game objects
        self.player_sprite = None
        self.held_keys = set()
        self.ground_list = None
        self.platform_list = None

        # Set background color
        arcade.set_background_color(arcade.color.AMAZON)

        # Player physics properties
        self.is_jumping = False
        self.vertical_velocity = 0

        # Viewport properties
        self.view_left = 0
        self.view_bottom = 0

        # Track the highest platform generated
        self.highest_platform_y = GROUND_HEIGHT

    def setup(self):
        # Set up the player
        self.player_sprite = arcade.Sprite("Images/pngegg.png", PLAYER_SCALE)
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = GROUND_HEIGHT

        # Set up the ground
        self.ground_list = arcade.SpriteList()
        ground = arcade.SpriteSolidColor(SCREEN_WIDTH, GROUND_HEIGHT, arcade.color.DARK_BROWN)
        ground.center_x = SCREEN_WIDTH // 2
        ground.center_y = GROUND_HEIGHT // 2
        self.ground_list.append(ground)

        # Set up platforms
        self.platform_list = arcade.SpriteList()

    def on_draw(self):
        # Draw the game objects
        arcade.start_render()
        self.ground_list.draw()
        self.platform_list.draw()
        self.player_sprite.draw()

    def on_update(self, delta_time):
        # Update the player's horizontal position
        self.player_sprite.change_x = 0
        if arcade.key.A in self.held_keys:
            self.player_sprite.change_x = -PLAYER_SPEED
        if arcade.key.D in self.held_keys:
            self.player_sprite.change_x = PLAYER_SPEED

        # Update the player's vertical position
        if self.is_jumping:
            self.vertical_velocity -= GRAVITY

        self.player_sprite.center_y += self.vertical_velocity
        
        # Check if the player hits the ground
        if self.player_sprite.center_y <= GROUND_HEIGHT:
            self.player_sprite.center_y = GROUND_HEIGHT
            self.is_jumping = False
            self.vertical_velocity = 0

        # Check for collisions with platforms
        platform_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.platform_list)
        if platform_hit_list and self.vertical_velocity < 0:
            self.player_sprite.center_y = platform_hit_list[0].top
            self.is_jumping = False
            self.vertical_velocity = 0

        # Check if the player leaves a platform
        if not platform_hit_list and self.player_sprite.center_y > GROUND_HEIGHT and not self.is_jumping:
            self.is_jumping = True
            self.vertical_velocity = 0

        # Generate new platforms as the player traverses upwards
        if self.player_sprite.center_y > self.highest_platform_y - SCREEN_HEIGHT // 2:
            new_platform_y = self.highest_platform_y + random.randint(100, 200)
            new_platform_x = random.randint(50, SCREEN_WIDTH - 50)
            self.generate_platform(new_platform_x, new_platform_y)
            self.highest_platform_y = new_platform_y

        self.player_sprite.center_x += self.player_sprite.change_x

        self.player_sprite.update()

        # Update the viewport to center on the player
        left_boundary = self.view_left + SCREEN_WIDTH // 4
        right_boundary = self.view_left + 3 * SCREEN_WIDTH // 4
        bottom_boundary = self.view_bottom + SCREEN_HEIGHT // 4
        top_boundary = self.view_bottom + 3 * SCREEN_HEIGHT // 4

        if self.player_sprite.center_x < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.center_x
        if self.player_sprite.center_x > right_boundary:
            self.view_left += self.player_sprite.center_x - right_boundary
        if self.player_sprite.center_y < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.center_y
        if self.player_sprite.center_y > top_boundary:
            self.view_bottom += self.player_sprite.center_y - top_boundary

        self.view_left = int(self.view_left)
        self.view_bottom = int(self.view_bottom)

        arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)

    def on_key_press(self, key, modifiers):
        # Add the key to the set of held keys
        self.held_keys.add(key)
        
        # Handle jumping
        if key == arcade.key.W and not self.is_jumping:
            self.is_jumping = True
            self.vertical_velocity = PLAYER_JUMP_SPEED

    def on_key_release(self, key, modifiers):
        # Remove the key from the set of held keys
        if key in self.held_keys:
            self.held_keys.remove(key)

    def generate_platform(self, x, y, width=200, height=20):
        # Generate a platform at the specified position
        platform = arcade.SpriteSolidColor(width, height, arcade.color.GRAY)
        platform.center_x = x
        platform.center_y = y
        self.platform_list.append(platform)

# Main code to run the game
def main():
    window = MyGame()
    window.setup()
    window.generate_platform(600, 400)
    window.generate_platform(800, 600)
    arcade.run()

if __name__ == "__main__":
    main()