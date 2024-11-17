# constants.py

# Screen constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Top-Down Shooter Game"

# Player constants
PLAYER_SCALING = 0.2
PLAYER_MOVEMENT_SPEED = 2
PLAYER_HEALTH = 100
PLAYER_FIRE_RATE = 15  # Frames between shots
PLAYER_BULLET_DAMAGE = 10
INITIAL_AMMO = 30

# Enemy constants
ENEMY_SCALING = 0.1
ENEMY_MOVEMENT_SPEED = 1
ENEMY_HEALTH = 50
ENEMY_SHOOT_RANGE = 200
ENEMY_DETECTION_RANGE = 400  # Detection range for enemies
ENEMY_SHOOT_DELAY = 30  # Frames between shots
ENEMY_BULLET_DAMAGE = 10
ENEMY_BULLET_SPEED = 5

# Cone constants
CONE_ANGLE = 30  # Half-angle in degrees
CONE_LENGTH = 300

# Ammo pickup constants
AMMO_PICKUP_AMOUNT = 10
AMMO_PICKUP_SCALING = 0.1

# World constants
WORLD_CENTER_X = 0
WORLD_CENTER_Y = 0
WORLD_RADIUS = 1000
SAFE_SPAWN_DISTANCE = 300  # Minimum distance from player to spawn enemies or pickups

# Boss constants
BOSS_SCALING = 0.3
BOSS_HEALTH = ENEMY_HEALTH * 10
BOSS_MOVEMENT_SPEED = 1.5
BOSS_SHOOT_RANGE = 300
BOSS_SHOOT_DELAY = 20  # Boss fires more frequently
BOSS_BULLET_DAMAGE = ENEMY_BULLET_DAMAGE * 2
BOSS_BULLET_SPEED = 7
HEALTH_PICKUP_AMOUNT = 50  # Amount of health restored by a health pickup


