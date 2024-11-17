# startup.py

import arcade
import arcade.gui
import main  # Import the main game module
from audio import AudioManager  # Import AudioManager

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Top-Down Shooter Game - Startup"

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

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        arcade.start_render()
        self.ui_manager.draw()
        arcade.draw_text(
            "Top-Down Shooter Game",
            self.window.width // 2,
            self.window.height - 100,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
        )

    def on_click_play(self, event):
        # Stop the startup sound
        self.audio_manager.stop_startup_sound()

        # Start the main game
        game_view = main.TopDownShooter()
        game_view.audio_manager = self.audio_manager  # Assign before setup()
        game_view.setup()
        self.window.show_view(game_view)
        self.ui_manager.disable()

    def on_click_quit(self, event):
        arcade.close_window()

    def on_hide_view(self):
        self.ui_manager.disable()

def run_main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
    startup_view = StartupView()
    window.show_view(startup_view)
    arcade.run()

if __name__ == "__main__":
    run_main()
