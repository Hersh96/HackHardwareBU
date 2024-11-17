import arcade
import arcade.gui
from audio import AudioManager  # Import AudioManager
import time
import math
from player import Player
from constants import PLAYER_SCALING

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Terrier Terror"

FLASHLIGHT_SCALING = 0.03  # Scale the flashlight sprite by this constant


class StartupView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the play button
        play_button = arcade.gui.UIFlatButton(text="Play", width=200)
        self.v_box.add(play_button.with_space_around(bottom=20))
        play_button.on_click = self.on_click_play

        # Create the quit button
        quit_button = arcade.gui.UIFlatButton(text="Quit", width=200)
        self.v_box.add(quit_button)
        quit_button.on_click = self.on_click_quit

        # Center the buttons
        self.ui_manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", child=self.v_box
            )
        )

        # Initialize AudioManager and play startup sound
        self.audio_manager = AudioManager()
        self.audio_manager.play_startup_sound()

        # Animation properties for the title
        self.title_scale = 1.0
        self.title_scale_direction = 1  # 1 for growing, -1 for shrinking
        self.title_color = (255, 255, 255)  # Initial color (white)
        self.title_color_shift = 0  # Incremental color shift

        # Flashlight dropping animation
        self.flashlight_dropping = False  # Flag for animation
        self.flashlight_sprite = arcade.Sprite(
            "resources/Images/flashlight.png", FLASHLIGHT_SCALING
        )  # Flashlight sprite
        self.flashlight_sprite.center_x = self.window.width // 2
        self.flashlight_sprite.center_y = self.window.height + 150  # Start flashlight above screen
        self.flashlight_on = False  # Initially turned off
        self.flashlight_radius = 300  # Light cone radius
        self.flashlight_speed = 2  # Horizontal speed of the flashlight
        self.flashlight_falling = False  # Stops horizontal movement once falling

        # Player sprite for reference
        self.player_sprite = Player(
            "resources/Images/top_View-removedbg.png",  # Standing texture
            "resources/Images/Moving1.png",             # Walking texture 1
            "resources/Images/Moving2.png",             # Walking texture 2
            PLAYER_SCALING,
        )
        self.player_sprite.center_x = 0  # Start player on the left side
        self.player_sprite.center_y = self.window.height // 2 - 150
        self.player_sprite.change_x = 0.9  # Movement speed

        # Transition effect properties
        self.transitioning = False
        self.transition_radius = 0

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        self.ui_manager.draw()

        # Draw the title
        self.draw_animated_title()

        # Draw the flashlight
        self.flashlight_sprite.draw()

        # Draw the transition effect under the player sprite
        self.draw_transition_effect()

        # Draw the player sprite (dog) on top
        self.player_sprite.draw()

    def draw_animated_title(self):
        """Draw the title with scaling and color effects."""
        # Scale the title up and down
        scale_speed = 0.005
        if self.title_scale >= 1.2:
            self.title_scale_direction = -1
        elif self.title_scale <= 0.8:
            self.title_scale_direction = 1
        self.title_scale += self.title_scale_direction * scale_speed

        # Shift the title color using a sine wave
        self.title_color_shift += 1
        red = int(128 + 127 * math.sin(math.radians(self.title_color_shift)))
        green = int(128 + 127 * math.sin(math.radians(self.title_color_shift + 120)))
        blue = int(128 + 127 * math.sin(math.radians(self.title_color_shift + 240)))
        self.title_color = (red, green, blue)

        # Draw the title
        arcade.draw_text(
            "Terrier Terror",
            self.window.width // 2,
            self.window.height // 2 + 100,
            self.title_color,
            font_size=30 * self.title_scale,
            anchor_x="center",
            font_name="Kenney Pixel",  # Optional fancy font
        )

    def draw_transition_effect(self):
        """Draw the circular transition effect."""
        arcade.draw_circle_filled(
            self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.transition_radius,
            arcade.color.BLACK,
        )

    def on_update(self, delta_time):
        """Update logic for animation."""
        # Player sprite movement
        self.player_sprite.update()
        self.player_sprite.center_x += self.player_sprite.change_x
        if self.player_sprite.center_x > self.window.width:
            self.player_sprite.center_x = self.window.width
            self.player_sprite.change_x *= -1  # Reverse direction
            self.player_sprite.scale *= -1  # Flip sprite
        elif self.player_sprite.center_x < 0:
            self.player_sprite.center_x = 0
            self.player_sprite.change_x *= -1  # Reverse direction
            self.player_sprite.scale *= -1  # Flip sprite

        # Flashlight horizontal movement (if not falling)
        if not self.flashlight_falling and not self.flashlight_dropping:
            self.flashlight_sprite.center_x += self.flashlight_speed
            if self.flashlight_sprite.center_x > self.window.width:
                self.flashlight_sprite.center_x = self.window.width
                self.flashlight_speed *= -1
            elif self.flashlight_sprite.center_x < 0:
                self.flashlight_sprite.center_x = 0
                self.flashlight_speed *= -1

        # Flashlight dropping animation
        if self.flashlight_dropping:
            self.flashlight_falling = True  # Stop horizontal movement
            self.flashlight_sprite.center_y -= 5
            if self.flashlight_sprite.center_y <= self.player_sprite.center_y:
                self.flashlight_sprite.center_y = self.player_sprite.center_y
                self.flashlight_dropping = False
                self.flashlight_on = True  # Flashlight picked up

        # Check if player has reached the flashlight
        if (
            abs(self.player_sprite.center_x - self.flashlight_sprite.center_x) < 20
            and abs(self.player_sprite.center_y - self.flashlight_sprite.center_y) < 20
        ):
            self.flashlight_on = True
            self.flashlight_sprite.remove_from_sprite_lists()
            self.player_sprite.remove_from_sprite_lists()
            self.start_transition_to_game()

        # Handle transition effect
        if self.transitioning:
            self.transition_radius += 20  # Increase the radius
            if self.transition_radius > max(self.window.width, self.window.height):
                self.transition_to_game()

    def start_transition_to_game(self):
        """Start the circular transition effect."""
        self.transitioning = True
        self.transition_radius = 0

    def on_resize(self, width, height):
        """Update boundaries dynamically when the window resizes."""
        self.player_sprite.center_y = height // 2 - 150
        self.flashlight_sprite.center_y = height + 150

    def on_click_play(self, event):
        """Handle the play button click."""
        self.audio_manager.stop_startup_sound()
        self.flashlight_dropping = True  # Start flashlight drop animation

    def on_click_quit(self, event):
        arcade.close_window()

    def transition_to_game(self):
        """Transition to the main game."""
        from main import TopDownShooter
        game_view = TopDownShooter()
        game_view.audio_manager = self.audio_manager
        game_view.setup()
        self.window.show_view(game_view)
        self.ui_manager.disable()

    def on_hide_view(self):
        self.ui_manager.disable()


class LoadingView(arcade.View):
    def __init__(self):
        super().__init__()
        self.loading_alpha = 0  # Transparency for "Loading..." animation
        self.fade_in = True  # Fade-in effect toggle
        self.start_time = time.time()  # Track loading start time
        self.assets_loaded = False  # Flag for asset loading completion

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()

        # Draw loading text
        self.draw_loading_animation()

        # Simulate asset loading or check if assets are ready
        self.simulate_asset_loading()

    def draw_loading_animation(self):
        """Draw the 'Loading...' text with a fade-in/out animation."""
        # Adjust alpha for fade-in/out
        if self.fade_in:
            self.loading_alpha += 3
            if self.loading_alpha >= 255:
                self.loading_alpha = 255
                self.fade_in = False
        else:
            self.loading_alpha -= 3
            if self.loading_alpha <= 100:
                self.loading_alpha = 100
                self.fade_in = True

        # Draw the "Loading..." text
        arcade.draw_text(
            "Loading...",
            self.window.width // 2,
            self.window.height // 2,
            (255, 255, 255, self.loading_alpha),  # White with transparency
            font_size=40,
            anchor_x="center",
            font_name="Kenney Pixel",  # Optional font
        )

    def simulate_asset_loading(self):
        """
        Simulate loading assets or perform actual loading logic.
        This example assumes a loading delay of 3 seconds.
        """
        if not self.assets_loaded:
            # Simulate a loading delay
            current_time = time.time()
            if current_time - self.start_time >= 2:  # Simulate a -second loading time
                self.assets_loaded = True

        # If assets are loaded, transition to the startup screen
        if self.assets_loaded:
            startup_view = StartupView()
            startup_view.audio_manager = AudioManager()  # Set up AudioManager for the next view
            self.window.show_view(startup_view)


def run_main():
    """Main entry point for the game."""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True, fullscreen=True)
    loading_view = LoadingView()
    window.show_view(loading_view)
    arcade.run()


if __name__ == "__main__":
    run_main()
