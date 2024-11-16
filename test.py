import arcade

# Constants for the game
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Simple Character Movement"
CHARACTER_SCALING = 0.5
GRAVITY = 1.0
JUMP_SPEED = 20
MOVEMENT_SPEED = 5

# Sprite image path (use a local placeholder or a valid online image link)
CHARACTER_SPRITE = "Images/pngegg.png"

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        
        # Sprite lists
        self.player_list = None
        
        # Player info
        self.player_sprite = None
        self.physics_engine = None

    def setup(self):
        # Set up the game here
        self.player_list = arcade.SpriteList()
        
        # Create the player character
        self.player_sprite = arcade.Sprite(CHARACTER_SPRITE, CHARACTER_SCALING)
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = 150
        self.player_list.append(self.player_sprite)

        # Ground
        self.ground = arcade.SpriteList()
        ground_sprite = arcade.SpriteSolidColor(SCREEN_WIDTH, 100, arcade.color.BROWN)
        ground_sprite.center_x = SCREEN_WIDTH // 2
        ground_sprite.center_y = 50
        self.ground.append(ground_sprite)

        # Set up physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.ground, gravity_constant=GRAVITY)

    def on_draw(self):
        arcade.start_render()
        # Draw all sprites
        self.player_list.draw()
        self.ground.draw()

    def on_key_press(self, key, modifiers):
        # Handle key presses
        if key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        # Handle key releases
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def update(self, delta_time):
        # Update game state
        self.physics_engine.update()

if __name__ == "__main__":
    game = MyGame()
    game.setup()
    arcade.run()
