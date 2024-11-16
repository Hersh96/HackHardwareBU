# main.py

import arcade
import random
import math
import arcade.gui

from constants import *
from enemy import Enemy
from player import Player
from bullet import Bullet
from ammo_pickup import AmmoPickup
from audio import AudioManager  # Import AudioManager

class TopDownShooter(arcade.View):
    def __init__(self):
        super().__init__()

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.ammo_pickup_list = arcade.SpriteList()

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

        # Audio Manager will be set in setup()
        self.audio_manager = None

        # Player death handling
        self.player_dead = False
        self.death_timer = 0

        # Enemies killed count
        self.enemies_killed = 0

    def setup(self):
        # Set background color
        arcade.set_background_color(arcade.color.AMAZON)

        # Create the player at the center of the world
        self.player_sprite = Player("../Images/top_View.jpg", PLAYER_SCALING)
        self.player_sprite.center_x = WORLD_CENTER_X
        self.player_sprite.center_y = WORLD_CENTER_Y
        self.player_list.append(self.player_sprite)

        # Spawn the initial wave of enemies
        self.spawn_enemies()

        # Ensure the startup sound is stopped and start the game sound
        if self.audio_manager:
            self.audio_manager.stop_startup_sound()
            self.audio_manager.play_game_sound()

    def on_show(self):
        self.window.set_mouse_visible(False)

    def on_draw(self):
        arcade.start_render()
        self.camera.use()

        # Draw the world boundary circle
        arcade.draw_circle_outline(
            WORLD_CENTER_X,
            WORLD_CENTER_Y,
            WORLD_RADIUS,
            arcade.color.WHITE,
            2
        )

        # Draw sprites
        self.player_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.ammo_pickup_list.draw()

        # Draw health and ammo
        self.draw_hud()

        # Draw cones
        self.draw_cones()

        # Draw arrows pointing towards enemies that haven't fired for 15 seconds
        self.draw_enemy_arrows()

    def draw_hud(self):
        # Player health bar
        arcade.draw_rectangle_filled(
            self.camera.position[0] + 100,
            self.camera.position[1] + self.window.height - 20,
            self.player_sprite.health,
            10,
            arcade.color.RED,
        )

        # Ammo counter
        ammo_text = f"Ammo: {self.player_sprite.ammo}"
        arcade.draw_text(
            ammo_text,
            self.camera.position[0] + 10,
            self.camera.position[1] + self.window.height - 40,
            arcade.color.WHITE,
            14,
        )

        # Wave number display
        wave_text = f"Wave: {self.wave_number}"
        arcade.draw_text(
            wave_text,
            self.camera.position[0] + self.window.width - 100,
            self.camera.position[1] + self.window.height - 40,
            arcade.color.WHITE,
            14,
            anchor_x="center"
        )

    def draw_cones(self):
        # Player cone
        self.draw_cone(
            self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.player_sprite.angle,
            CONE_LENGTH,
            CONE_ANGLE,
            arcade.color.YELLOW,
        )

        # Enemy cones
        for enemy in self.enemy_list:
            self.draw_cone(
                enemy.center_x,
                enemy.center_y,
                enemy.angle,
                ENEMY_SHOOT_RANGE,
                CONE_ANGLE,
                arcade.color.RED,
            )

    def draw_cone(self, start_x, start_y, facing_angle, cone_length, cone_angle, color):
        left_angle = math.radians(facing_angle + cone_angle)
        right_angle = math.radians(facing_angle - cone_angle)

        end_x1 = start_x + math.cos(left_angle) * cone_length
        end_y1 = start_y + math.sin(left_angle) * cone_length
        end_x2 = start_x + math.cos(right_angle) * cone_length
        end_y2 = start_y + math.sin(right_angle) * cone_length

        arcade.draw_line(start_x, start_y, end_x1, end_y1, color, 2)
        arcade.draw_line(start_x, start_y, end_x2, end_y2, color, 2)
        arcade.draw_arc_filled(
            start_x,
            start_y,
            cone_length * 2,
            cone_length * 2,
            color + (50,),
            facing_angle - cone_angle,
            facing_angle + cone_angle,
        )

    def draw_enemy_arrows(self):
        for enemy in self.enemy_list:
            # Check if time since last fire exceeds 15 seconds (assuming 60 FPS)
            if enemy.time_since_last_fire >= 15 * 60:
                self.draw_arrow_towards_enemy(enemy)

    def draw_arrow_towards_enemy(self, enemy):
        # Calculate the direction vector from the player to the enemy
        dx = enemy.center_x - self.player_sprite.center_x
        dy = enemy.center_y - self.player_sprite.center_y
        distance = math.hypot(dx, dy)

        # Normalize the direction vector
        if distance != 0:
            dx /= distance
            dy /= distance

        # Set the arrow length (e.g., 50 pixels)
        arrow_length = 50

        # Calculate the arrow position starting from the player
        start_x = self.player_sprite.center_x + dx * 100  # Offset from the player
        start_y = self.player_sprite.center_y + dy * 100

        end_x = start_x + dx * arrow_length
        end_y = start_y + dy * arrow_length

        # Calculate the angle of the arrow
        angle = math.degrees(math.atan2(dy, dx))

        # Draw the arrow
        arcade.draw_line(start_x, start_y, end_x, end_y, arcade.color.GREEN, 4)
        # Draw the arrowhead
        size = 10
        arcade.draw_triangle_filled(
            end_x, end_y,
            end_x - size * math.cos(math.radians(angle + 135)),
            end_y - size * math.sin(math.radians(angle + 135)),
            end_x - size * math.cos(math.radians(angle - 135)),
            end_y - size * math.sin(math.radians(angle - 135)),
            arcade.color.GREEN
        )

    def on_update(self, delta_time):
        if self.player_dead:
            # Increment death timer
            self.death_timer += delta_time
            # Assuming dying sound is 3 seconds
            if self.death_timer >= 3.0:
                # Switch to game over view
                game_over_view = GameOverView(self.enemies_killed)
                self.window.show_view(game_over_view)
            return  # Skip updating the game

        # Update sprites
        self.player_list.update()
        self.enemy_list.update()
        self.bullet_list.update()
        self.ammo_pickup_list.update()

        # Update camera to follow player, constrained within the world circle
        cam_x = self.player_sprite.center_x - self.window.width / 2
        cam_y = self.player_sprite.center_y - self.window.height / 2

        # Calculate camera's distance from the world center
        dx = cam_x + self.window.width / 2 - WORLD_CENTER_X
        dy = cam_y + self.window.height / 2 - WORLD_CENTER_Y
        distance = math.hypot(dx, dy)
        max_distance = WORLD_RADIUS - max(self.window.width, self.window.height) / 2

        if distance > max_distance:
            angle = math.atan2(dy, dx)
            cam_x = WORLD_CENTER_X + max_distance * math.cos(angle) - self.window.width / 2
            cam_y = WORLD_CENTER_Y + max_distance * math.sin(angle) - self.window.height / 2

        self.camera.move_to((cam_x, cam_y), 0.1)

        # Update player angle
        dx = self.mouse_x - self.player_sprite.center_x
        dy = self.mouse_y - self.player_sprite.center_y
        self.player_sprite.angle = math.degrees(math.atan2(dy, dx))

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

        # Handle player shooting
        self.handle_player_shooting()

        # Handle ammo pickups
        self.handle_ammo_pickups()

        # Handle player walking sound
        if self.audio_manager:
            if self.player_sprite.change_x != 0 or self.player_sprite.change_y != 0:
                self.audio_manager.play_player_walk_sound()
            else:
                self.audio_manager.stop_player_walk_sound()

        # Check for wave completion
        if not self.enemy_list:
            self.wave_number += 1
            self.spawn_enemies()

    def keep_sprite_within_world(self, sprite):
        dx = sprite.center_x - WORLD_CENTER_X
        dy = sprite.center_y - WORLD_CENTER_Y
        distance = math.hypot(dx, dy)
        if distance > WORLD_RADIUS:
            angle = math.atan2(dy, dx)
            sprite.center_x = WORLD_CENTER_X + WORLD_RADIUS * math.cos(angle)
            sprite.center_y = WORLD_CENTER_Y + WORLD_RADIUS * math.sin(angle)

    def spawn_enemies(self):
        if self.wave_number == 1:
            num_enemies = 1
        else:
            enemy_counts = [1, 2, 3, 4, 5, 6]
            # Calculate weights based on wave number
            weights = [count ** (self.wave_number - 2) for count in enemy_counts]
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            # Select the number of enemies based on the calculated weights
            num_enemies = random.choices(enemy_counts, weights=weights, k=1)[0]

        for _ in range(num_enemies):
            enemy_sprite = Enemy("../Images/enemy.png", ENEMY_SCALING)
            # Increase enemy health per wave (optional)
            enemy_sprite.health = ENEMY_HEALTH + (self.wave_number - 1) * 10

            # Generate a random position within the circle and outside the safe spawn distance
            while True:
                angle = random.uniform(0, 2 * math.pi)
                r = WORLD_RADIUS * math.sqrt(random.uniform(0, 1))
                x = WORLD_CENTER_X + r * math.cos(angle)
                y = WORLD_CENTER_Y + r * math.sin(angle)

                # Check distance from player
                distance_to_player = math.hypot(
                    x - self.player_sprite.center_x, y - self.player_sprite.center_y
                )
                if distance_to_player >= SAFE_SPAWN_DISTANCE:
                    break  # Found a valid position

            enemy_sprite.center_x = x
            enemy_sprite.center_y = y
            self.enemy_list.append(enemy_sprite)

    def spawn_ammo_pickup(self):
        # Generate a random position within the circle
        while True:
            angle = random.uniform(0, 2 * math.pi)
            r = WORLD_RADIUS * math.sqrt(random.uniform(0, 1))
            x = WORLD_CENTER_X + r * math.cos(angle)
            y = WORLD_CENTER_Y + r * math.sin(angle)
            # Check distance from player
            distance_to_player = math.hypot(
                x - self.player_sprite.center_x, y - self.player_sprite.center_y
            )
            if distance_to_player >= SAFE_SPAWN_DISTANCE:
                break  # Found a valid position
        ammo_pickup = AmmoPickup(5, arcade.color.BLUE, x, y)
        self.ammo_pickup_list.append(ammo_pickup)

    def handle_bullets(self):
        for bullet in self.bullet_list:
            # Remove bullets outside the world
            dx = bullet.center_x - WORLD_CENTER_X
            dy = bullet.center_y - WORLD_CENTER_Y
            distance = math.hypot(dx, dy)
            if distance > WORLD_RADIUS:
                bullet.remove_from_sprite_lists()
                continue

            if bullet.owner == 'player':
                # Check collision with enemies
                hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
                for enemy in hit_list:
                    enemy.health -= PLAYER_BULLET_DAMAGE
                    bullet.remove_from_sprite_lists()
                    if enemy.health <= 0:
                        # Enemy dies
                        self.spawn_ammo_pickup_at(enemy.center_x, enemy.center_y)
                        enemy.remove_from_sprite_lists()
                        self.enemies_killed += 1  # Increment enemies killed
                        # Play enemy die sound
                        if self.audio_manager:
                            self.audio_manager.play_enemy_die_sound()
                    else:
                        # Play player hit enemy sound
                        if self.audio_manager:
                            self.audio_manager.play_player_kill_enemy_sound()
                    break  # Bullet is gone, no need to check further
            elif bullet.owner == 'enemy':
                # Check collision with player
                if arcade.check_for_collision(bullet, self.player_sprite):
                    self.player_sprite.health -= ENEMY_BULLET_DAMAGE
                    bullet.remove_from_sprite_lists()
                    if self.player_sprite.health <= 0:
                        # Player dies
                        if self.audio_manager:
                            self.audio_manager.stop_game_sound()
                            self.audio_manager.stop_player_walk_sound()
                            self.audio_manager.stop_enemy_near_player_sound()
                            self.audio_manager.play_player_die_sound()
                        self.player_dead = True
                        self.death_timer = 0
                        self.player_sprite.remove_from_sprite_lists()
                    break  # Bullet is gone, no need to check further

    def spawn_ammo_pickup_at(self, x, y):
        ammo_pickup = AmmoPickup(5, arcade.color.BLUE, x, y)
        self.ammo_pickup_list.append(ammo_pickup)

    def handle_enemies(self):
        enemy_near_player = False
        for enemy in self.enemy_list:
            # Keep enemy within world circle
            self.keep_sprite_within_world(enemy)

            distance_to_player = arcade.get_distance_between_sprites(
                enemy, self.player_sprite
            )

            if distance_to_player <= ENEMY_DETECTION_RANGE:
                enemy_near_player = True  # At least one enemy is near
                # Enemy detects player, follows the player
                dx = self.player_sprite.center_x - enemy.center_x
                dy = self.player_sprite.center_y - enemy.center_y
                enemy.angle = math.degrees(math.atan2(dy, dx))

                if distance_to_player > ENEMY_SHOOT_RANGE:
                    # Move towards player
                    enemy.change_x = ENEMY_MOVEMENT_SPEED * math.cos(
                        math.radians(enemy.angle)
                    )
                    enemy.change_y = ENEMY_MOVEMENT_SPEED * math.sin(
                        math.radians(enemy.angle)
                    )
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
                        ):
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
                # Change direction randomly
                if random.random() < 0.02:
                    enemy.change_x = random.uniform(-ENEMY_MOVEMENT_SPEED, ENEMY_MOVEMENT_SPEED)
                    enemy.change_y = random.uniform(-ENEMY_MOVEMENT_SPEED, ENEMY_MOVEMENT_SPEED)
                # Update enemy's angle based on movement direction
                if enemy.change_x != 0 or enemy.change_y != 0:
                    enemy.angle = math.degrees(math.atan2(enemy.change_y, enemy.change_x))

                # Increment time since last fire
                enemy.time_since_last_fire += 1

            # Apply movement
            enemy.update()

        # Play or stop the enemy near player sound
        if self.audio_manager:
            if enemy_near_player:
                self.audio_manager.play_enemy_near_player_sound()
            else:
                self.audio_manager.stop_enemy_near_player_sound()

    def handle_player_shooting(self):
        # Reduce shoot timer
        if self.player_sprite.shoot_timer > 0:
            self.player_sprite.shoot_timer -= 1

        # Check for shooting
        for enemy in self.enemy_list:
            if self.is_within_cone(
                self.player_sprite,
                enemy.center_x,
                enemy.center_y,
                self.player_sprite.angle,
                CONE_LENGTH,
                CONE_ANGLE,
            ):
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
                    break  # Only shoot one bullet per update

    def handle_ammo_pickups(self):
        # Collect ammo pickups
        ammo_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.ammo_pickup_list
        )
        for ammo in ammo_hit_list:
            self.player_sprite.ammo += AMMO_PICKUP_AMOUNT
            ammo.remove_from_sprite_lists()
            # Optionally, play a sound effect here

    def is_within_cone(
        self, sprite, target_x, target_y, facing_angle, cone_length, cone_angle
    ):
        dx = target_x - sprite.center_x
        dy = target_y - sprite.center_y
        distance = math.hypot(dx, dy)
        angle_to_target = math.degrees(math.atan2(dy, dx))
        angle_difference = abs((angle_to_target - facing_angle + 180) % 360 - 180)
        return distance < cone_length and angle_difference < cone_angle

    def on_key_press(self, key, modifiers):
        if key in [arcade.key.UP, arcade.key.W]:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key in [arcade.key.DOWN, arcade.key.S]:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key in [arcade.key.LEFT, arcade.key.A]:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key in [arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.UP, arcade.key.W]:
            self.player_sprite.change_y = 0
        elif key in [arcade.key.DOWN, arcade.key.S]:
            self.player_sprite.change_y = 0
        elif key in [arcade.key.LEFT, arcade.key.A]:
            self.player_sprite.change_x = 0
        elif key in [arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = 0

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x + self.camera.position[0]
        self.mouse_y = y + self.camera.position[1]

    def on_resize(self, width, height):
        self.camera.resize(int(width), int(height))

class GameOverView(arcade.View):
    def __init__(self, enemies_killed):
        super().__init__()
        self.enemies_killed = enemies_killed

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
        # Draw the number of enemies killed
        arcade.draw_text(
            f"Enemies Killed: {self.enemies_killed}",
            self.window.width // 2,
            self.window.height - 150,
            arcade.color.WHITE,
            font_size=20,
            anchor_x="center",
        )

    def on_click_replay(self, event):
        # Restart the game
        game_view = TopDownShooter()
        game_view.setup()
        # Create a new AudioManager instance
        game_view.audio_manager = AudioManager()
        game_view.audio_manager.play_game_sound()
        self.window.show_view(game_view)
        self.ui_manager.disable()

    def on_click_quit(self, event):
        arcade.close_window()

    def on_hide_view(self):
        self.ui_manager.disable()

def run_game():
    # The game is started from startup.py, so run_game() is not needed here.
    pass

if __name__ == "__main__":
    run_game()
