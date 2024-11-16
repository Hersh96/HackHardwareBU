# main.py

import arcade
import random
import math

from constants import *
from enemy import Enemy
from player import Player
from bullet import Bullet
from ammo_pickup import AmmoPickup

class TopDownShooter(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)

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
        self.camera = arcade.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Ammo spawn timer
        self.ammo_spawn_timer = 0

    def setup(self):
        # Set background color
        arcade.set_background_color(arcade.color.AMAZON)

        # Create the player
        self.player_sprite = Player("Images/top_view.png", PLAYER_SCALING)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_list.append(self.player_sprite)

        # Create an enemy
        enemy_sprite = Enemy("Images/enemy.png", ENEMY_SCALING)
        enemy_sprite.center_x = random.randint(0, SCREEN_WIDTH)
        enemy_sprite.center_y = random.randint(0, SCREEN_HEIGHT)
        self.enemy_list.append(enemy_sprite)

    def on_draw(self):
        arcade.start_render()
        self.camera.use()

        # Draw sprites
        self.player_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.ammo_pickup_list.draw()

        # Draw health and ammo
        self.draw_hud()

        # Draw cones
        self.draw_cones()

    def draw_hud(self):
        # Player health bar
        arcade.draw_rectangle_filled(
            self.camera.position[0] + 100,
            self.camera.position[1] + SCREEN_HEIGHT - 20,
            self.player_sprite.health,
            10,
            arcade.color.RED,
        )

        # Ammo counter
        ammo_text = f"Ammo: {self.player_sprite.ammo}"
        arcade.draw_text(
            ammo_text,
            self.camera.position[0] + 10,
            self.camera.position[1] + SCREEN_HEIGHT - 40,
            arcade.color.WHITE,
            14,
        )

    def draw_cones(self):
        # Player cone
        self.draw_cone(
            self.player_sprite.center_x,
            self.player_sprite.center_y,
            self.mouse_x,
            self.mouse_y,
            arcade.color.YELLOW,
        )

        # Enemy cones
        for enemy in self.enemy_list:
            self.draw_cone(
                enemy.center_x,
                enemy.center_y,
                self.player_sprite.center_x,
                self.player_sprite.center_y,
                arcade.color.RED,
            )

    def draw_cone(self, start_x, start_y, target_x, target_y, color):
        angle_radians = math.atan2(target_y - start_y, target_x - start_x)

        left_angle = angle_radians + math.radians(CONE_ANGLE)
        right_angle = angle_radians - math.radians(CONE_ANGLE)

        end_x1 = start_x + math.cos(left_angle) * CONE_LENGTH
        end_y1 = start_y + math.sin(left_angle) * CONE_LENGTH
        end_x2 = start_x + math.cos(right_angle) * CONE_LENGTH
        end_y2 = start_y + math.sin(right_angle) * CONE_LENGTH

        arcade.draw_line(start_x, start_y, end_x1, end_y1, color, 2)
        arcade.draw_line(start_x, start_y, end_x2, end_y2, color, 2)
        arcade.draw_arc_filled(
            start_x,
            start_y,
            CONE_LENGTH * 2,
            CONE_LENGTH * 2,
            color + (50,),
            math.degrees(right_angle),
            math.degrees(left_angle),
        )

    def spawn_ammo_pickup(self):
        # Count ammo pickups in FOV
        ammo_in_fov = sum(
            1 for ammo in self.ammo_pickup_list if self.is_within_cone(
                self.player_sprite, ammo.center_x, ammo.center_y, self.mouse_x, self.mouse_y
            )
        )

        if ammo_in_fov < 3:
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            ammo_pickup = AmmoPickup(5, arcade.color.BLUE, x, y)
            self.ammo_pickup_list.append(ammo_pickup)

    def on_update(self, delta_time):
        # Update sprites
        self.player_list.update()
        self.enemy_list.update()
        self.bullet_list.update()
        self.ammo_pickup_list.update()

        # Update camera
        self.camera.move_to(
            (
                self.player_sprite.center_x - SCREEN_WIDTH / 2,
                self.player_sprite.center_y - SCREEN_HEIGHT / 2,
            ),
            0.1,
        )

        # Update player angle
        dx = self.mouse_x - self.player_sprite.center_x
        dy = self.mouse_y - self.player_sprite.center_y
        self.player_sprite.angle = math.degrees(math.atan2(dy, dx))

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

    def handle_bullets(self):
        for bullet in self.bullet_list:
            # Remove bullets off-screen
            if (
                bullet.center_x < 0
                or bullet.center_x > SCREEN_WIDTH
                or bullet.center_y < 0
                or bullet.center_y > SCREEN_HEIGHT
            ):
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
                    break  # Bullet is gone, no need to check further
            elif bullet.owner == 'enemy':
                # Check collision with player
                if arcade.check_for_collision(bullet, self.player_sprite):
                    self.player_sprite.health -= ENEMY_BULLET_DAMAGE
                    bullet.remove_from_sprite_lists()
                    if self.player_sprite.health <= 0:
                        print("Game Over")
                        arcade.close_window()
                    break  # Bullet is gone, no need to check further

    def spawn_ammo_pickup_at(self, x, y):
        ammo_pickup = AmmoPickup(5, arcade.color.BLUE, x, y)
        self.ammo_pickup_list.append(ammo_pickup)

    def handle_enemies(self):
        for enemy in self.enemy_list:
            distance_to_player = arcade.get_distance_between_sprites(enemy, self.player_sprite)

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
                        self.player_sprite.center_x,
                        self.player_sprite.center_y,
                        CONE_LENGTH=ENEMY_SHOOT_RANGE,
                    ):
                        bullet = Bullet(5, arcade.color.RED, 'enemy', ENEMY_BULLET_SPEED)
                        bullet.center_x = enemy.center_x
                        bullet.center_y = enemy.center_y
                        bullet.angle = math.degrees(
                            math.atan2(
                                self.player_sprite.center_y - enemy.center_y,
                                self.player_sprite.center_x - enemy.center_x,
                            )
                        )
                        bullet.change_x = math.cos(math.radians(bullet.angle)) * bullet.speed
                        bullet.change_y = math.sin(math.radians(bullet.angle)) * bullet.speed
                        self.bullet_list.append(bullet)
                        enemy.shoot_timer = ENEMY_SHOOT_DELAY

            # Decrease shoot timer
            if enemy.shoot_timer > 0:
                enemy.shoot_timer -= 1

            # Update enemy angle towards player
            enemy.angle = math.degrees(
                math.atan2(
                    self.player_sprite.center_y - enemy.center_y,
                    self.player_sprite.center_x - enemy.center_x,
                )
            )

    def handle_player_shooting(self):
        # Reduce shoot timer
        if self.player_sprite.shoot_timer > 0:
            self.player_sprite.shoot_timer -= 1

        # Check for shooting
        for enemy in self.enemy_list:
            if self.is_within_cone(
                self.player_sprite, enemy.center_x, enemy.center_y, self.mouse_x, self.mouse_y
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
                else:
                    # No ammo or still in cooldown
                    pass

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
        self, sprite, target_x, target_y, direction_x, direction_y, CONE_LENGTH=CONE_LENGTH
    ):
        dx = target_x - sprite.center_x
        dy = target_y - sprite.center_y
        distance = math.sqrt(dx**2 + dy**2)
        angle_to_target = math.degrees(math.atan2(dy, dx))
        angle_to_direction = math.degrees(
            math.atan2(direction_y - sprite.center_y, direction_x - sprite.center_x)
        )
        angle_difference = abs((angle_to_target - angle_to_direction + 180) % 360 - 180)

        return distance < CONE_LENGTH and angle_difference < CONE_ANGLE

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

def main():
    window = TopDownShooter()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
