# audio.py

import arcade

class AudioManager:
    def __init__(self):
        # Load sounds
        self.startup_sound = arcade.load_sound("sounds/startup_sound.mp3")
        self.game_sound = arcade.load_sound("sounds/game_sound.mp3")
        self.player_walk_sound = arcade.load_sound("sounds/player_walk.mp3")
        self.player_kill_enemy_sound = arcade.load_sound("sounds/player_kill_enemy.mp3")
        self.enemy_near_player_sound = arcade.load_sound("sounds/enemy_near_player.mp3")
        self.enemy_die_sound = arcade.load_sound("sounds/enemy_die.mp3")
        self.player_die_sound = arcade.load_sound("sounds/player_die.mp3")
        self.boss_sound = arcade.load_sound("sounds/boss_sound.mp3")  # Load boss sound

        # Keep track of sound players for looping sounds
        self.startup_sound_player = None
        self.game_sound_player = None
        self.player_walk_sound_player = None
        self.enemy_near_sound_player = None
        self.boss_sound_player = None  # Player for boss sound

        # Keep track of dying sound players
        self.enemy_die_sound_player = None
        self.player_die_sound_player = None

    def play_startup_sound(self):
        if self.startup_sound_player is None or not self.startup_sound_player.playing:
            self.startup_sound_player = arcade.play_sound(self.startup_sound)

    def stop_startup_sound(self):
        if self.startup_sound_player is not None:
            self.startup_sound_player.pause()
            self.startup_sound_player.seek(0.0)
            self.startup_sound_player = None

    def play_game_sound(self):
        if self.game_sound_player is None or not self.game_sound_player.playing:
            self.game_sound_player = self.game_sound.play(loop=True)

    def stop_game_sound(self):
        if self.game_sound_player is not None:
            self.game_sound_player.pause()
            self.game_sound_player.seek(0.0)
            self.game_sound_player = None

    def play_player_walk_sound(self):
        if self.player_walk_sound_player is None or not self.player_walk_sound_player.playing:
            self.player_walk_sound_player = self.player_walk_sound.play(loop=False)

    def stop_player_walk_sound(self):
        if self.player_walk_sound_player is not None:
            self.player_walk_sound_player.pause()
            self.player_walk_sound_player.seek(0.0)
            self.player_walk_sound_player = None

    def play_player_kill_enemy_sound(self):
        arcade.play_sound(self.player_kill_enemy_sound)

    def play_enemy_near_player_sound(self):
        if self.enemy_near_sound_player is None or not self.enemy_near_sound_player.playing:
            self.enemy_near_sound_player = self.enemy_near_player_sound.play(loop=False)

    def stop_enemy_near_player_sound(self):
        if self.enemy_near_sound_player is not None:
            self.enemy_near_sound_player.pause()
            self.enemy_near_sound_player.seek(0.0)
            self.enemy_near_sound_player = None

    def play_enemy_die_sound(self):
        if self.enemy_die_sound_player is not None:
            self.enemy_die_sound_player.pause()
            self.enemy_die_sound_player.seek(0.0)
        self.enemy_die_sound_player = arcade.play_sound(self.enemy_die_sound)

    def stop_enemy_die_sound(self):
        if self.enemy_die_sound_player is not None:
            self.enemy_die_sound_player.pause()
            self.enemy_die_sound_player.seek(0.0)
            self.enemy_die_sound_player = None

    def play_player_die_sound(self):
        if self.player_die_sound_player is not None:
            self.player_die_sound_player.pause()
            self.player_die_sound_player.seek(0.0)
        self.player_die_sound_player = arcade.play_sound(self.player_die_sound)

    def stop_player_die_sound(self):
        if self.player_die_sound_player is not None:
            self.player_die_sound_player.pause()
            self.player_die_sound_player.seek(0.0)
            self.player_die_sound_player = None

    def play_boss_sound(self):
        if self.boss_sound_player is None or not self.boss_sound_player.playing:
            self.boss_sound_player = self.boss_sound.play(volume=0.5, loop=True)

    def stop_boss_sound(self):
        if self.boss_sound_player is not None and self.boss_sound_player.playing:
            self.boss_sound_player.pause()
            self.boss_sound_player = None

    def stop_all_sounds(self):
        """Stop all active sounds."""
        if self:
            self.stop_startup_sound()
            self.stop_game_sound()
            self.stop_boss_sound()
            self.stop_player_walk_sound()
            self.stop_enemy_near_player_sound()
            self.stop_player_die_sound()
            self.stop_enemy_die_sound()
