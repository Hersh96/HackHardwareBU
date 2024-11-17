import os
import sys
import arcade
import random
import math
import arcade.gui
import json
from itertools import chain  # Import chain to combine SpriteLists

from constants import *
from enemy import Enemy
from boss import Boss  # Import the Boss class
from player import Player
from bullet import Bullet
from ammo_pickup import AmmoPickup
from audio import AudioManager
from wall import Wall

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)
    
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
        # Stop all other sounds
        if self.audio_manager:
            self.audio_manager.stop_game_sound()
            self.audio_manager.stop_boss_sound()
            self.audio_manager.stop_player_walk_sound()
            self.audio_manager.stop_enemy_near_player_sound()

            # Play startup music
            self.audio_manager.play_startup_sound()

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
        # Stop startup music and transition to the game
        if self.audio_manager:
            self.audio_manager.stop_startup_sound()

        game_view = TopDownShooter()
        game_view.audio_manager = self.audio_manager
        game_view.setup()
        self.window.show_view(game_view)
        self.ui_manager.disable()

    def on_click_quit(self, event):
        """Quit the application."""
        # Stop all sounds when quitting
        if self.audio_manager:
            self.audio_manager.stop_all_sounds()
        arcade.close_window()

    def on_hide_view(self):
        self.ui_manager.disable()

class PauseMenuView(arcade.View):
    def __init__(self, main_game_view):
        super().__init__()
        self.main_game_view = main_game_view  # Reference to the main game view
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the resume button
        resume_button = arcade.gui.UIFlatButton(text="Resume", width=200)
        self.v_box.add(resume_button.with_space_around(bottom=20))
        resume_button.on_click = self.on_click_resume

        # Create the restart button
        restart_button = arcade.gui.UIFlatButton(text="Restart", width=200)
        self.v_box.add(restart_button.with_space_around(bottom=20))
        restart_button.on_click = self.on_click_restart

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

    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_BLUE)

    def on_draw(self):
        arcade.start_render()
        self.ui_manager.draw()

        # Draw the "Paused" text
        arcade.draw_text(
            "Paused",
            self.window.width // 2,
            self.window.height - 100,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
        )

    def on_click_resume(self, event):
        """Resume the game."""
        self.ui_manager.disable()
        self.window.show_view(self.main_game_view)

    def on_click_restart(self, event):
        """Restart the game from Wave 1."""
        self.ui_manager.disable()
        new_game_view = TopDownShooter()
        new_game_view.audio_manager = self.main_game_view.audio_manager
        new_game_view.setup()  # Start fresh from Wave 1
        self.window.show_view(new_game_view)

    def on_click_quit(self, event):
        """Return to the main menu."""
        self.ui_manager.disable()
        if self.main_game_view.audio_manager:
            if self.main_game_view.audio_manager:
                self.main_game_view.audio_manager.stop_all_sounds()

            # Play startup music
            self.main_game_view.audio_manager.play_startup_sound()

        main_menu_view = MainMenuView(self.main_game_view.audio_manager)
        self.window.show_view(main_menu_view)




    def on_hide_view(self):
        self.ui_manager.disable()


class TopDownShooter(arcade.View):
    def __init__(self):
        super().__init__()
        self.pressed_keys = set()  # To track currently pressed keys
        self.show_tutorial = True  # Show tutorial text initially
        self.tutorial_timer = 0    # Timer to hide the tutorial text

        self.key_w = arcade.Sprite(":resources:images/items/keyBlue.png", scale=0.5)
        self.key_a = arcade.Sprite(":resources:images/items/keyBlue.png", scale=0.5)
        self.key_s = arcade.Sprite(":resources:images/items/keyBlue.png", scale=0.5)
        self.key_d = arcade.Sprite(":resources:images/items/keyBlue.png", scale=0.5)
        self.mouse_icon = arcade.Sprite(":resources:images/enemies/mouse.png", scale=0.3)

        self.key_w.center_x, self.key_w.center_y = 400, 400
        self.key_a.center_x, self.key_a.center_y = 350, 350
        self.key_s.center_x, self.key_s.center_y = 400, 300
        self.key_d.center_x, self.key_d.center_y = 450, 350
        self.mouse_icon.center_x, self.mouse_icon.center_y = 600, 350

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.boss_list = arcade.SpriteList()  # New list for bosses
        self.bullet_list = arcade.SpriteList()
        self.ammo_pickup_list = arcade.SpriteList()
        self.health_pickup_list = arcade.SpriteList()  # New list for health pickups
        self.wall_list = arcade.SpriteList()

        # Initialize player
        self.player_sprite = None

        # Mouse position
        self.mouse_x = 0
        self.mouse_y = 0

        # Camera
        self.camera = arcade.Camera(self.window.width, self.window.height)

        # Ammo spawn timer
        self.ammo_spawn_timer = 0

        # Wave number
        self.wave_number = 1

        # Audio Manager will be set before setup()
        self.audio_manager = AudioManager()  # Initialize AudioManager
        self.audio_manager.play_game_sound()

        # Player death handling
        self.player_dead = False
        self.death_timer = 0

        # Enemies killed count
        self.enemies_killed = 0

        # Boss defeated count
        self.bosses_defeated = 0

        # High score (total enemies and bosses defeated)
        self.high_score = 0

        # Flag to check if boss is active
        self.boss_active = False

        # Enable enemy ray casting
        self.enable_enemy_ray_casting = False

    def draw_tutorial_text(self):
        """
        Display a fancy tutorial with icons and text.
        """
        # Draw a semi-transparent background
        arcade.draw_rectangle_filled(
            self.camera.position[0] + self.window.width / 2,
            self.camera.position[1] + self.window.height / 2,
            700, 400,
            (0, 0, 0, 200)
        )

        # Draw instructional text
        tutorial_lines = [
            "Use WASD to move.",
            "Aim with your mouse cursor.",
            "Shooting is automatic.",
            "Collect ammo (Blue Orbs)",
            "Enemies drop ammo and health(only when player is at 10HP).",
            "Green arrows show enemy positions after 20 seconds.",
            "Wave 5 is a boss level(Full HP on defeating boss).",
            "Each wave has more enemies. Survive as long as you can!",
        ]
        screen_center_x = self.camera.position[0] + self.window.width / 2
        screen_center_y = self.camera.position[1] + self.window.height / 2
        y_offset = 100  # Start drawing text higher up on the screen

        for line in tutorial_lines:
            arcade.draw_text(
                line,
                screen_center_x,
                screen_center_y + y_offset,
                arcade.color.WHITE,
                font_size=16,
                font_name="Arial",
                anchor_x="center"
            )
            y_offset -= 30  # Move each line down by 30 pixels

        # Draw the control icons
        self.key_w.draw()
        self.key_a.draw()
        self.key_s.draw()
        self.key_d.draw()
        self.mouse_icon.draw()

        # Label the mouse icon
        arcade.draw_text(
            "Mouse",
            self.mouse_icon.center_x,
            self.mouse_icon.center_y - 40,
            arcade.color.WHITE,
            font_size=14,
            anchor_x="center",
            font_name="Arial",
        )

        # Label the WASD keys
        arcade.draw_text(
            "W", self.key_w.center_x, self.key_w.center_y, arcade.color.WHITE, font_size=16, anchor_x="center"
        )
        arcade.draw_text(
            "A", self.key_a.center_x, self.key_a.center_y, arcade.color.WHITE, font_size=16, anchor_x="center"
        )
        arcade.draw_text(
            "S", self.key_s.center_x, self.key_s.center_y, arcade.color.WHITE, font_size=16, anchor_x="center"
        )
        arcade.draw_text(
            "D", self.key_d.center_x, self.key_d.center_y, arcade.color.WHITE, font_size=16, anchor_x="center"
        )


    def setup(self):
        # Set background colordddd
        arcade.set_background_color((60, 60, 60, 255))

        # Create the player at the center of the world
        self.player_sprite = Player(
            "resources/Images/top_View-removedbg.png",  # Standing texture
            "resources/Images/Moving1.png",             # First walking frame
            "resources/Images/Moving2.png",             # Second walking frame
            PLAYER_SCALING,
        )
        self.player_sprite.center_x = WORLD_CENTER_X
        self.player_sprite.center_y = WORLD_CENTER_Y
        self.player_list.append(self.player_sprite)

        # Spawn the initial wave of enemies
        self.spawn_enemies()

        self.load_map("resources/assets/map1.json")

    
    def pause_game(self):
        """Pause the game and show the pause menu."""
        pause_view = PauseMenuView(self)
        self.window.show_view(pause_view)

    def on_show(self):
        self.window.set_mouse_visible(True)

    def spawn_enemies(self):
        if self.wave_number % 5 == 0 and not self.boss_active:
            # Spawn the boss
            self.spawn_boss()
            self.boss_active = True
        else:
            # Spawn regular enemies
            num_enemies = self.wave_number
            for _ in range(num_enemies):
                enemy_sprite = Enemy(
                    "resources/Images/enemy.png",          # Standing texture
                    "resources/Images/enemy.png",          # First walking frame (reused)
                    "resources/Images/enemy.png",          # Second walking frame (reused)
                    ENEMY_SCALING,
                )
                enemy_sprite.health = ENEMY_HEALTH + (self.wave_number - 1) * 10

                while True:
                    angle = random.uniform(0, 2 * math.pi)
                    r = WORLD_RADIUS * math.sqrt(random.uniform(0, 1))
                    x = WORLD_CENTER_X + r * math.cos(angle)
                    y = WORLD_CENTER_Y + r * math.sin(angle)

                    distance_to_player = math.hypot(
                        x - self.player_sprite.center_x, y - self.player_sprite.center_y
                    )
                    if distance_to_player >= SAFE_SPAWN_DISTANCE:
                        break

                enemy_sprite.center_x = x
                enemy_sprite.center_y = y
                self.enemy_list.append(enemy_sprite)

    def spawn_boss(self):
        boss_sprite = Boss(
            "resources/Images/boss.png",  # Path to the boss image
            "resources/Images/boss.png",
            "resources/Images/boss.png",
            BOSS_SCALING,
        )
        boss_sprite.health = BOSS_HEALTH
        boss_sprite.center_x = WORLD_CENTER_X
        boss_sprite.center_y = WORLD_CENTER_Y - 400  # Spawn position
        self.boss_list.append(boss_sprite)

        # Play the boss sound
        if self.audio_manager:
            self.audio_manager.play_boss_sound()

    def spawn_ammo_pickup_at(self, x, y):
        ammo_pickup = AmmoPickup(5, arcade.color.BLUE, x, y)
        self.ammo_pickup_list.append(ammo_pickup)

    def spawn_health_pickup_at(self, x, y):
        health_pickup = AmmoPickup(5, arcade.color.GREEN, x, y)
        self.health_pickup_list.append(health_pickup)

    def spawn_ammo_pickup(self):
        while True:
            angle = random.uniform(0, 2 * math.pi)
            r = WORLD_RADIUS * math.sqrt(random.uniform(0, 1))
            x = WORLD_CENTER_X + r * math.cos(angle)
            y = WORLD_CENTER_Y + r * math.sin(angle)

            distance_to_player = math.hypot(
                x - self.player_sprite.center_x, y - self.player_sprite.center_y
            )
            if distance_to_player >= SAFE_SPAWN_DISTANCE:
                break

        ammo_pickup = AmmoPickup(5, arcade.color.BLUE, x, y)
        self.ammo_pickup_list.append(ammo_pickup)

    def draw_outside_world_background(self):
        
        screen_width, screen_height = self.window.get_size()
        arcade.draw_rectangle_filled(
            self.camera.position[0] + screen_width / 2,
            self.camera.position[1] + screen_height / 2,
            screen_width,
            screen_height,
            arcade.color.DARK_BLUE,  # Background color for outside world
        )


    def on_draw(self):
        arcade.start_render()
        self.camera.use()

        # Draw the background outside the world boundary
        self.draw_outside_world_background()

        

        # Draw the world circle
        arcade.draw_circle_filled(
            WORLD_CENTER_X,
            WORLD_CENTER_Y,
            WORLD_RADIUS,
            (60, 60, 60, 255)  # World color (matches the existing background)
        )

        # Draw the dark overlay first
        self.draw_dark_overlay()

        # Draw the world circle outline
        arcade.draw_circle_outline(
            WORLD_CENTER_X,
            WORLD_CENTER_Y,
            WORLD_RADIUS,
            arcade.color.WHITE,
            3,
        )

        # Draw flashlight effect for the player
        self.draw_light_cone(
            self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.player_sprite.angle,
            CONE_LENGTH,
            CONE_ANGLE,
            (180, 180, 180, 100)  # Light yellow with transparency
        )

        # Conditionally draw flashlight effects for all enemies
        if self.enable_enemy_ray_casting:
            for enemy in self.enemy_list:
                self.draw_light_cone(
                    enemy.center_x,
                    enemy.center_y,
                    enemy.angle,
                    ENEMY_SHOOT_RANGE,
                    CONE_ANGLE,
                    (255, 0, 0, 50),  # Light red with transparency
                )
            for boss in self.boss_list:
                self.draw_light_cone(
                    boss.center_x,
                    boss.center_y,
                    boss.angle,
                    BOSS_SHOOT_RANGE,
                    CONE_ANGLE,
                    (128, 0, 128, 50),  # Light purple with transparency
                )

        # Draw visible objects in cones
        self.draw_visible_objects()

        # Draw all sprites and HUD elements on the top-most layer
        self.player_list.draw()
        self.enemy_list.draw()
        self.boss_list.draw()
        self.bullet_list.draw()
        self.ammo_pickup_list.draw()
        self.health_pickup_list.draw()
        self.draw_hud()
        self.draw_enemy_arrows()
        if self.wave_number == 1 and self.show_tutorial:
            self.draw_tutorial_text()

    def draw_dark_overlay(self):
        """
        Create a full-screen dark overlay to simulate limited vision.
        """
        screen_width, screen_height = self.window.width, self.window.height
        arcade.draw_lrtb_rectangle_filled(
            self.camera.position[0],
            self.camera.position[0] + screen_width,
            self.camera.position[1] + screen_height,
            self.camera.position[1],
            (0, 0, 0, 150)  # Dark overlay with alpha for transparency
        )

    def draw_light_cone(self, start_x, start_y, facing_angle, cone_length, cone_angle, color):
        step_angle = 1  # Adjust for smoother rendering
        ray_points = []

        for angle_offset in range(-cone_angle // 2, cone_angle // 2 + 1, step_angle):
            angle = facing_angle + angle_offset
            end_point = self.cast_ray(start_x, start_y, angle, cone_length, self.wall_list)
            ray_points.append(end_point)

        # Draw the flashlight cone with transparency
        for i in range(len(ray_points) - 1):
            arcade.draw_triangle_filled(
                start_x, start_y,
                ray_points[i][0], ray_points[i][1],
                ray_points[i + 1][0], ray_points[i + 1][1],
                color
            )

    def draw_visible_objects(self):
        """
        Draw visible objects (including walls) dynamically based on visibility.
        """
        visible_objects = self.get_visible_objects()

        # Highlight and draw visible walls above the overlay
        for obj in visible_objects:
            if obj in self.wall_list:
                obj.color = arcade.color.WHITE  # Highlight visible walls
            obj.draw()

        # Draw invisible walls (dimmed) below the overlay
        for wall in self.wall_list:
            if wall not in visible_objects:
                wall.color = arcade.color.GRAY  # Dim invisible walls
                wall.draw()

    def get_visible_objects(self):
        visible_objects = []

        # Check objects within the player's cone
        visible_objects.extend(self.get_objects_in_cone(
            self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.player_sprite.angle,
            CONE_LENGTH,
            CONE_ANGLE
        ))

        # Check objects within each enemy's cone
        for enemy in self.enemy_list:
            visible_objects.extend(self.get_objects_in_cone(
                enemy.center_x,
                enemy.center_y,
                enemy.angle,
                ENEMY_SHOOT_RANGE,
                CONE_ANGLE
            ))

        # Check objects within each boss's cone
        for boss in self.boss_list:
            visible_objects.extend(self.get_objects_in_cone(
                boss.center_x,
                boss.center_y,
                boss.angle,
                BOSS_SHOOT_RANGE,
                CONE_ANGLE
            ))

        return visible_objects

    def get_objects_in_cone(self, start_x, start_y, facing_angle, cone_length, cone_angle):
        visible_objects = []

        # Combine all relevant sprite lists into a single iterable
        all_objects = list(self.wall_list) + list(self.ammo_pickup_list) + list(self.health_pickup_list) + list(self.enemy_list) + list(self.boss_list)

        for obj in all_objects:
            if self.is_object_visible_in_cone(start_x, start_y, facing_angle, obj, cone_length, cone_angle):
                visible_objects.append(obj)

        return visible_objects

    def has_line_of_sight(self, shooter, target, wall_list):
        """
        Check if there is a clear line of sight between shooter and target, unobstructed by walls.
        """
        ray_line = [(shooter.center_x, shooter.center_y), (target.center_x, target.center_y)]
        for wall in wall_list:
            for wall_line in wall.get_lines():
                if self.get_line_intersection(ray_line, wall_line):
                    return False
        return True

    def is_object_visible_in_cone(self, start_x, start_y, facing_angle, obj, cone_length, cone_angle):
        """
        Check if an object is visible within a cone.
        """
        dx = obj.center_x - start_x
        dy = obj.center_y - start_y
        distance = math.hypot(dx, dy)
        angle_to_object = math.degrees(math.atan2(dy, dx))
        angle_difference = abs((angle_to_object - facing_angle + 180) % 360 - 180)

        # Check if the object is within the cone's range and angle
        if distance < cone_length and angle_difference < cone_angle / 2:
            # Ensure the object is not obscured by a wall
            return self.has_line_of_sight_to_point(start_x, start_y, obj.center_x, obj.center_y)
        return False

    def has_line_of_sight_to_point(self, start_x, start_y, end_x, end_y):
        """
        Check if there is a clear line of sight to a point (end_x, end_y) from (start_x, start_y).
        """
        ray_line = [(start_x, start_y), (end_x, end_y)]

        # Check for intersection with walls
        for wall in self.wall_list:
            for wall_line in wall.get_lines():
                if self.get_line_intersection(ray_line, wall_line):
                    return False

        return True

    def get_line_intersection(self, line1, line2):
        """
        Finds the intersection point of two lines if it exists.
        Each line is defined as [(x1, y1), (x2, y2)].
        Returns the intersection point (x, y) or None if no intersection exists.
        """
        x1, y1 = line1[0]
        x2, y2 = line1[1]
        x3, y3 = line2[0]
        x4, y4 = line2[1]

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None  # Lines are parallel or coincident

        intersect_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
        intersect_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

        # Check if the intersection point is within both line segments
        if (
            min(x1, x2) <= intersect_x <= max(x1, x2)
            and min(y1, y2) <= intersect_y <= max(y1, y2)
            and min(x3, x4) <= intersect_x <= max(x3, x4)
            and min(y3, y4) <= intersect_y <= max(y3, y4)
        ):
            return (intersect_x, intersect_y)

        return None  # No valid intersection within the segments

    def cast_ray(self, start_x, start_y, angle, max_length, wall_list):
        """
        Cast a ray from (start_x, start_y) in the given angle up to max_length, stopping at walls.
        Returns the endpoint of the ray.
        """
        end_x = start_x + math.cos(math.radians(angle)) * max_length
        end_y = start_y + math.sin(math.radians(angle)) * max_length

        ray_line = [(start_x, start_y), (end_x, end_y)]
        closest_distance = max_length
        closest_point = (end_x, end_y)

        # Check for intersection with walls
        for wall in wall_list:
            for wall_line in wall.get_lines():  # Wall defines its edges as line segments
                intersection = self.get_line_intersection(ray_line, wall_line)
                if intersection:
                    distance = math.hypot(intersection[0] - start_x, intersection[1] - start_y)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_point = intersection

        # Ensure the ray stops exactly at the wall boundary
        if closest_distance < max_length:
            end_x = start_x + math.cos(math.radians(angle)) * closest_distance
            end_y = start_y + math.sin(math.radians(angle)) * closest_distance

        return (end_x, end_y)

    def draw_enemy_arrows(self):
        for enemy in self.enemy_list:
            # Check if time since last fire exceeds 15 seconds (assuming 60 FPS)
            if enemy.time_since_last_fire >= 15 * 60:
                self.draw_arrow_towards_enemy(enemy)
        for boss in self.boss_list:
            if boss.time_since_last_fire >= 15 * 60:
                self.draw_arrow_towards_enemy(boss)

    def draw_arrow_towards_enemy(self, enemy):
        # Calculate the direction vector from the player to the enemy
        dx = enemy.center_x - self.player_sprite.center_x
        dy = enemy.center_y - self.player_sprite.center_y
        distance = math.hypot(dx, dy)

        if distance == 0:
            return  # Avoid division by zero

        # Normalize the direction vector
        dx /= distance
        dy /= distance

        # Set the arrow length
        arrow_length = 50

        # Start position at the edge of the screen in the direction of the enemy
        screen_width, screen_height = self.window.get_size()
        screen_center_x = self.camera.position[0] + screen_width / 2
        screen_center_y = self.camera.position[1] + screen_height / 2

        # Calculate the angle to the enemy
        angle = math.atan2(dy, dx)

        # Determine the edge point
        edge_x, edge_y = self.get_point_on_screen_edge(
            angle, screen_center_x, screen_center_y, screen_width, screen_height
        )

        # Draw the arrow pointing towards the enemy
        end_x = edge_x - dx * arrow_length
        end_y = edge_y - dy * arrow_length

        arcade.draw_line(edge_x, edge_y, end_x, end_y, arcade.color.GREEN, 4)

        # Draw the arrowhead
        size = 10
        arcade.draw_triangle_filled(
            edge_x,
            edge_y,
            edge_x - size * math.cos(angle + math.pi / 6),
            edge_y - size * math.sin(angle + math.pi / 6),
            edge_x - size * math.cos(angle - math.pi / 6),
            edge_y - size * math.sin(angle - math.pi / 6),
            arcade.color.GREEN,
        )

    def get_point_on_screen_edge(self, angle, center_x, center_y, width, height):
        tan_theta = math.tan(angle)
        if -math.pi / 2 <= angle <= math.pi / 2:
            x = center_x + width / 2
            y = center_y + (width / 2) * tan_theta
            if y > center_y + height / 2:
                y = center_y + height / 2
                x = center_x + (height / 2) / tan_theta
        else:
            x = center_x - width / 2
            y = center_y - (width / 2) * tan_theta
            if y < center_y - height / 2:
                y = center_y - height / 2
                x = center_x - (height / 2) / tan_theta
        return x, y

    def load_map(self, map_file):
        # Clear existing walls
        self.wall_list = arcade.SpriteList()

        # Load the map data
        with open(map_file, "r") as f:
            map_data = json.load(f)

        for wall_data in map_data["walls"]:
            x, y = wall_data["x"], wall_data["y"]
            width, height = wall_data["width"], wall_data["height"]

            # Check if the wall is within the circular world boundary
            dx = x - WORLD_CENTER_X
            dy = y - WORLD_CENTER_Y
            if math.hypot(dx, dy) + max(width, height) / 2 <= WORLD_RADIUS:
                wall = Wall(width, height, arcade.color.GRAY, x, y)
                self.wall_list.append(wall)

    def draw_hud(self):
        # Draw player health bar
        health_percentage = self.player_sprite.health / PLAYER_HEALTH
        health_bar_width = 200 * health_percentage
        arcade.draw_rectangle_filled(
            self.camera.position[0] + health_bar_width / 2 + 10,
            self.camera.position[1] + self.window.height - 20,
            health_bar_width,
            10,
            arcade.color.RED,
        )
        # Draw health text
        health_text = f"Health: {self.player_sprite.health}/{PLAYER_HEALTH}"
        arcade.draw_text(
            health_text,
            self.camera.position[0] + 10,
            self.camera.position[1] + self.window.height - 40,
            arcade.color.WHITE,
            14,
        )

        # Draw ammo count
        ammo_text = f"Ammo: {self.player_sprite.ammo}"
        arcade.draw_text(
            ammo_text,
            self.camera.position[0] + 10,
            self.camera.position[1] + self.window.height - 60,
            arcade.color.WHITE,
            14,
        )

        # Draw wave number
        wave_text = f"Wave: {self.wave_number}"
        arcade.draw_text(
            wave_text,
            self.camera.position[0] + self.window.width - 100,
            self.camera.position[1] + self.window.height - 40,
            arcade.color.WHITE,
            14,
            anchor_x="center",
        )

    def on_update(self, delta_time):
        if self.wave_number == 1 and self.show_tutorial:
            self.tutorial_timer += delta_time
            if self.tutorial_timer > 11:  # Hide tutorial after 10 seconds
                self.show_tutorial = False
        if self.player_dead:
            # Stop boss sound if player dies
            if self.audio_manager:
                self.audio_manager.stop_boss_sound()
            # Increment death timer
            self.death_timer += delta_time
            if self.death_timer >= 3.0:
                # Calculate high score
                self.high_score = self.enemies_killed + self.bosses_defeated * 50
                # Switch to game over view, passing audio_manager
                game_over_view = GameOverView(self.high_score, self.audio_manager)
                self.window.show_view(game_over_view)
            return

        # Update sprites
        self.player_list.update()
        self.enemy_list.update()
        self.boss_list.update()
        self.bullet_list.update()
        self.ammo_pickup_list.update()
        self.health_pickup_list.update()

        # Check for collisions with walls
        if arcade.check_for_collision_with_list(self.player_sprite, self.wall_list):
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0

        # Update camera to follow player, constrained within the world circle
        cam_x = self.player_sprite.center_x - self.window.width / 2
        cam_y = self.player_sprite.center_y - self.window.height / 2

        dx = cam_x + self.window.width / 2 - WORLD_CENTER_X
        dy = cam_y + self.window.height / 2 - WORLD_CENTER_Y
        distance = math.hypot(dx, dy)
        max_distance = WORLD_RADIUS * 1.5 - max(self.window.width, self.window.height) / 2

        if distance > max_distance:
            angle = math.atan2(dy, dx)
            cam_x = WORLD_CENTER_X + max_distance * math.cos(angle) - self.window.width / 2
            cam_y = WORLD_CENTER_Y + max_distance * math.sin(angle) - self.window.height / 2

        self.camera.move_to((cam_x, cam_y), 0.1)

        # Smoothly rotate the player to face the mouse pointer
        target_angle = math.degrees(
            math.atan2(
                self.mouse_y - self.player_sprite.center_y,
                self.mouse_x - self.player_sprite.center_x,
            )
        )
        current_angle = self.player_sprite.angle

        # Calculate the shortest rotation direction
        angle_diff = (target_angle - current_angle + 180) % 360 - 180

        # Set a rotation speed
        rotation_speed = 300 * delta_time  # Degrees per second

        # Update the angle with a clamped rotation
        if abs(angle_diff) < rotation_speed:
            self.player_sprite.angle = target_angle
        else:
            self.player_sprite.angle += rotation_speed * (1 if angle_diff > 0 else -1)

        # Keep player within world circle
        self.keep_sprite_within_world(self.player_sprite)

        # Spawn ammo pickups
        self.ammo_spawn_timer += 1
        if self.ammo_spawn_timer >= 120:
            self.spawn_ammo_pickup()
            self.ammo_spawn_timer = 0

        # Handle bullets
        self.handle_bullets()

        # Handle enemies
        self.handle_enemies()

        # Handle bosses
        self.handle_bosses()

        # Handle player shooting
        self.handle_player_shooting()

        # Handle pickups
        self.handle_pickups()

        # Handle player walking sound
        if self.audio_manager:
            if self.player_sprite.change_x != 0 or self.player_sprite.change_y != 0:
                self.audio_manager.play_player_walk_sound()
            else:
                self.audio_manager.stop_player_walk_sound()

        # Check for wave completion
        if not self.enemy_list and not self.boss_list:
            self.wave_number += 1
            self.boss_active = False
            self.spawn_enemies()

    def keep_sprite_within_world(self, sprite):
        dx = sprite.center_x - WORLD_CENTER_X
        dy = sprite.center_y - WORLD_CENTER_Y
        distance = math.hypot(dx, dy)
        if distance > WORLD_RADIUS:
            angle = math.atan2(dy, dx)
            sprite.center_x = WORLD_CENTER_X + WORLD_RADIUS * math.cos(angle)
            sprite.center_y = WORLD_CENTER_Y + WORLD_RADIUS * math.sin(angle)

    def handle_bullets(self):
        for bullet in self.bullet_list:
            # Remove bullets that leave the world boundary
            dx = bullet.center_x - WORLD_CENTER_X
            dy = bullet.center_y - WORLD_CENTER_Y
            distance = math.hypot(dx, dy)
            if distance > WORLD_RADIUS:
                bullet.remove_from_sprite_lists()
                continue

            # Check if the bullet hits a wall
            walls_hit = arcade.check_for_collision_with_list(bullet, self.wall_list)
            if walls_hit:
                bullet.remove_from_sprite_lists()
                continue

            if bullet.owner == 'player':
                hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
                hit_list += arcade.check_for_collision_with_list(bullet, self.boss_list)
                for target in hit_list:
                    if isinstance(target, Enemy):
                        target.health -= PLAYER_BULLET_DAMAGE
                        bullet.remove_from_sprite_lists()
                        if target.health <= 0:
                            self.enemies_killed += 1
                            # Drop health pack if player's health is below 20
                            if self.player_sprite.health < 20:
                                self.spawn_health_pickup_at(target.center_x, target.center_y)
                            else:
                                self.spawn_ammo_pickup_at(target.center_x, target.center_y)
                            target.remove_from_sprite_lists()
                            if self.audio_manager:
                                self.audio_manager.play_enemy_die_sound()
                        else:
                            # Play player hit enemy sound
                            if self.audio_manager:
                                self.audio_manager.play_player_kill_enemy_sound()
                        break  # Only one collision per bullet

                    elif isinstance(target, Boss):
                        target.health -= PLAYER_BULLET_DAMAGE
                        bullet.remove_from_sprite_lists()
                        if target.health <= 0:
                            self.bosses_defeated += 1
                            # Restore player's health to full
                            self.player_sprite.health = PLAYER_HEALTH
                            target.remove_from_sprite_lists()
                            if self.audio_manager:
                                self.audio_manager.play_enemy_die_sound()
                                self.audio_manager.stop_boss_sound()  # Stop boss sound
                        else:
                            # Play player hit boss sound
                            if self.audio_manager:
                                self.audio_manager.play_player_kill_enemy_sound()
                        break  # Only one collision per bullet
            elif bullet.owner == 'enemy':
                if arcade.check_for_collision(bullet, self.player_sprite):
                    self.player_sprite.health -= ENEMY_BULLET_DAMAGE
                    bullet.remove_from_sprite_lists()
                    if self.player_sprite.health <= 0:
                        self.player_sprite.texture = self.player_sprite.dead_texture
                        if self.audio_manager:
                            self.audio_manager.stop_game_sound()
                            self.audio_manager.stop_player_walk_sound()
                            self.audio_manager.stop_enemy_near_player_sound()
                            self.audio_manager.play_player_die_sound()
                            self.audio_manager.stop_boss_sound()
                        self.player_dead = True
                        self.death_timer = 0
                        # self.player_sprite.remove_from_sprite_lists()
                        break
            elif bullet.owner == 'boss':
                if arcade.check_for_collision(bullet, self.player_sprite):
                    self.player_sprite.health -= BOSS_BULLET_DAMAGE
                    bullet.remove_from_sprite_lists()
                    if self.player_sprite.health <= 0:
                        self.player_sprite.texture = self.player_sprite.dead_texture
                        if self.audio_manager:
                            self.audio_manager.stop_game_sound()
                            self.audio_manager.stop_player_walk_sound()
                            self.audio_manager.stop_enemy_near_player_sound()
                            self.audio_manager.play_player_die_sound()
                            self.audio_manager.stop_boss_sound()
                        self.player_dead = True
                        self.death_timer = 0
                        # self.player_sprite.remove_from_sprite_lists()
                        break

    def handle_player_shooting(self):
        if self.player_sprite.shoot_timer > 0:
            self.player_sprite.shoot_timer -= 1

        # Combine enemy and boss lists into a single iterable
        targets = chain(self.enemy_list, self.boss_list)

        for target in targets:
            if self.is_within_cone(
                self.player_sprite,
                target.center_x,
                target.center_y,
                self.player_sprite.angle,
                CONE_LENGTH,
                CONE_ANGLE,
            ) and self.has_line_of_sight(self.player_sprite, target, self.wall_list):
                if self.player_sprite.ammo > 0 and self.player_sprite.shoot_timer <= 0:
                    bullet = Bullet(5, arcade.color.YELLOW, 'player', 10)
                    bullet.center_x = self.player_sprite.center_x
                    bullet.center_y = self.player_sprite.center_y
                    bullet.angle = self.player_sprite.angle
                    bullet.change_x = math.cos(math.radians(bullet.angle)) * bullet.speed
                    bullet.change_y = math.sin(math.radians(bullet.angle)) * bullet.speed
                    self.bullet_list.append(bullet)
                    self.player_sprite.shoot_timer = PLAYER_FIRE_RATE
                    self.player_sprite.ammo -= 1
                    break  # Shoot only once per update

    def is_within_cone(self, sprite, target_x, target_y, facing_angle, cone_length, cone_angle):
        dx = target_x - sprite.center_x
        dy = target_y - sprite.center_y
        distance = math.hypot(dx, dy)
        angle_to_target = math.degrees(math.atan2(dy, dx))
        angle_difference = abs((angle_to_target - facing_angle + 180) % 360 - 180)
        return distance < cone_length and angle_difference < (cone_angle / 2)

    def on_key_press(self, key, modifiers):

        self.pressed_keys.add(key)
        self.update_movement()

        # Pause the game when ESC is pressed
        if key == arcade.key.ESCAPE:
            self.pause_game()

    def on_key_release(self, key, modifiers):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
        self.update_movement()

    def update_movement(self):
        # Reset movement
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        # Check for movement keys in the set
        if arcade.key.UP in self.pressed_keys or arcade.key.W in self.pressed_keys:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        if arcade.key.DOWN in self.pressed_keys or arcade.key.S in self.pressed_keys:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        if arcade.key.LEFT in self.pressed_keys or arcade.key.A in self.pressed_keys:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        if arcade.key.RIGHT in self.pressed_keys or arcade.key.D in self.pressed_keys:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x + self.camera.position[0]
        self.mouse_y = y + self.camera.position[1]

    def on_resize(self, width, height):
        self.camera.resize(int(width), int(height))

    def handle_enemies(self):
        enemy_near_player = False
        for enemy in self.enemy_list:
            # Keep enemy within world circle
            self.keep_sprite_within_world(enemy)

            # Handle collision with walls
            enemy.handle_collision(self.wall_list)

            distance_to_player = arcade.get_distance_between_sprites(enemy, self.player_sprite)

            if distance_to_player <= ENEMY_DETECTION_RANGE:
                enemy_near_player = True  # At least one enemy is near
                # Enemy detects player, follows the player
                dx = self.player_sprite.center_x - enemy.center_x
                dy = self.player_sprite.center_y - enemy.center_y
                enemy.angle = math.degrees(math.atan2(dy, dx))

                if distance_to_player > ENEMY_SHOOT_RANGE:
                    # Move towards player
                    enemy.change_x = ENEMY_MOVEMENT_SPEED * math.cos(math.radians(enemy.angle))
                    enemy.change_y = ENEMY_MOVEMENT_SPEED * math.sin(math.radians(enemy.angle))
                else:
                    # Stop movement
                    enemy.change_x = 0
                    enemy.change_y = 0

                    # Shoot at player
                    if enemy.shoot_timer <= 0:
                        if self.is_within_cone(
                            enemy,
                            self.player_sprite.center_x,
                            self.player_sprite.center_y,
                            enemy.angle,
                            ENEMY_SHOOT_RANGE,
                            CONE_ANGLE,
                        ) and self.has_line_of_sight(enemy, self.player_sprite, self.wall_list):
                            bullet = Bullet(5, arcade.color.RED, 'enemy', ENEMY_BULLET_SPEED)
                            bullet.center_x = enemy.center_x
                            bullet.center_y = enemy.center_y
                            bullet.angle = enemy.angle
                            bullet.change_x = math.cos(math.radians(bullet.angle)) * bullet.speed
                            bullet.change_y = math.sin(math.radians(bullet.angle)) * bullet.speed
                            self.bullet_list.append(bullet)
                            enemy.shoot_timer = ENEMY_SHOOT_DELAY

                            # Reset the time since last fire
                            enemy.time_since_last_fire = 0
                    else:
                        # Enemy cannot fire yet
                        enemy.shoot_timer -= 1
                        # Increment time since last fire
                        enemy.time_since_last_fire += 1
                # Increment time since last fire if enemy didn't shoot
                if enemy.shoot_timer > 0:
                    enemy.time_since_last_fire += 1
            else:
                # Enemy is too far from player, move randomly
                if random.random() < 0.02:
                    enemy.change_x = random.uniform(-ENEMY_MOVEMENT_SPEED, ENEMY_MOVEMENT_SPEED)
                    enemy.change_y = random.uniform(-ENEMY_MOVEMENT_SPEED, ENEMY_MOVEMENT_SPEED)
                if enemy.change_x != 0 or enemy.change_y != 0:
                    enemy.angle = math.degrees(math.atan2(enemy.change_y, enemy.change_x))

                enemy.time_since_last_fire += 1

            # Apply movement
            enemy.update()

        # Play or stop the enemy near player sound
        if self.audio_manager:
            if enemy_near_player:
                self.audio_manager.play_enemy_near_player_sound()
            else:
                self.audio_manager.stop_enemy_near_player_sound()

    def handle_bosses(self):
        for boss in self.boss_list:
            # Keep boss within world circle
            self.keep_sprite_within_world(boss)

            # Handle collision with walls
            boss.handle_collision(self.wall_list)

            distance_to_player = arcade.get_distance_between_sprites(boss, self.player_sprite)

            # Boss always follows the player
            dx = self.player_sprite.center_x - boss.center_x
            dy = self.player_sprite.center_y - boss.center_y
            boss.angle = math.degrees(math.atan2(dy, dx))

            if distance_to_player > BOSS_SHOOT_RANGE:
                # Move towards player
                boss.change_x = BOSS_MOVEMENT_SPEED * math.cos(math.radians(boss.angle))
                boss.change_y = BOSS_MOVEMENT_SPEED * math.sin(math.radians(boss.angle))
            else:
                # Stop movement
                boss.change_x = 0
                boss.change_y = 0

                # Shoot at player
                if boss.shoot_timer <= 0:
                    if self.is_within_cone(
                        boss,
                        self.player_sprite.center_x,
                        self.player_sprite.center_y,
                        boss.angle,
                        BOSS_SHOOT_RANGE,
                        CONE_ANGLE,
                    ) and self.has_line_of_sight(boss, self.player_sprite, self.wall_list):
                        bullet = Bullet(7, arcade.color.PURPLE, 'boss', BOSS_BULLET_SPEED)
                        bullet.center_x = boss.center_x
                        bullet.center_y = boss.center_y
                        bullet.angle = boss.angle
                        bullet.change_x = math.cos(math.radians(bullet.angle)) * bullet.speed
                        bullet.change_y = math.sin(math.radians(bullet.angle)) * bullet.speed
                        self.bullet_list.append(bullet)
                        boss.shoot_timer = BOSS_SHOOT_DELAY

                        # Reset the time since last fire
                        boss.time_since_last_fire = 0
                else:
                    # Boss cannot fire yet
                    boss.shoot_timer -= 1
                    # Increment time since last fire
                    boss.time_since_last_fire += 1

            # Apply movement
            boss.update()

    def handle_pickups(self):
        # Ammo pickups
        ammo_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.ammo_pickup_list
        )
        for ammo in ammo_hit_list:
            self.player_sprite.ammo += AMMO_PICKUP_AMOUNT
            ammo.remove_from_sprite_lists()

        # Health pickups
        health_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.health_pickup_list
        )
        for health in health_hit_list:
            self.player_sprite.health += HEALTH_PICKUP_AMOUNT
            if self.player_sprite.health > PLAYER_HEALTH:
                self.player_sprite.health = PLAYER_HEALTH  # Cap at max health
            health.remove_from_sprite_lists()


class GameOverView(arcade.View):
    def __init__(self, high_score, audio_manager):
        super().__init__()
        self.high_score = high_score
        self.audio_manager = audio_manager  # Store the audio_manager

        # UI manager for buttons
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Create the replay button
        replay_button = arcade.gui.UIFlatButton(text="Replay", width=200)
        self.v_box.add(replay_button.with_space_around(bottom=20))
        replay_button.on_click = self.on_click_replay

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

    def on_show(self):
        arcade.set_background_color(arcade.color.BLACK)
        self.window.set_mouse_visible(True)

    def on_draw(self):
        arcade.start_render()
        self.ui_manager.draw()
        # Draw the "Game Over" text
        arcade.draw_text(
            "Game Over",
            self.window.width // 2,
            self.window.height - 100,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
        )
        # Draw the high score
        arcade.draw_text(
            f"High Score: {self.high_score}",
            self.window.width // 2,
            self.window.height - 150,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
        )

    def on_click_replay(self, event):
        # Stop any dying sounds
        if self.audio_manager:
            self.audio_manager.stop_player_die_sound()
            self.audio_manager.stop_enemy_die_sound()

        # Restart the game
        game_view = TopDownShooter()
        # Reuse the existing AudioManager instance
        game_view.audio_manager = self.audio_manager
        game_view.setup()
        self.window.show_view(game_view)
        self.ui_manager.disable()

    def on_click_quit(self, event):
        """Return to the main menu."""
        if self.audio_manager:
            # Stop all sounds
            self.audio_manager.stop_all_sounds()

            # Play startup music
            self.audio_manager.play_startup_sound()

        main_menu_view = MainMenuView(self.audio_manager)
        self.window.show_view(main_menu_view)
        self.ui_manager.disable()



    def on_hide_view(self):
        # Stop any dying sounds
        if self.audio_manager:
            self.audio_manager.stop_player_die_sound()
            self.audio_manager.stop_enemy_die_sound()
        self.ui_manager.disable()


def run_game():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Top-Down Shooter")
    start_view = TopDownShooter()
    start_view.setup()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    run_game()
