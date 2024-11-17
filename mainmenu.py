import arcade
from audio import AudioManager
from main import TopDownShooter


class MainMenuView(arcade.View):
    def __init__(self, audio_manager=None):
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

        # Use the existing AudioManager if provided
        self.audio_manager = audio_manager or AudioManager()

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.window.set_mouse_visible(True)

    def on_draw(self):
        arcade.start_render()
        self.ui_manager.draw()

        # Draw the title
        arcade.draw_text(
            "Terrier Terror",
            self.window.width // 2,
            self.window.height - 100,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
            font_name="Kenney Pixel",  # Optional font
        )

    def on_click_play(self, event):
        """Start the main game."""
        game_view = TopDownShooter()
        game_view.audio_manager = self.audio_manager
        game_view.setup()
        self.window.show_view(game_view)
        self.ui_manager.disable()

    def on_click_quit(self, event):
        """Quit the application."""
        arcade.close_window()

    def on_hide_view(self):
        self.ui_manager.disable()
