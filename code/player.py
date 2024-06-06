import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    """
    The Player class represents the player character in the game.

    Attributes:
        frames (dict): A dictionary of lists containing the player's animation frames.
        state (str): The current state (direction) of the player.
        frame_index (int): The current frame index for animation.
        image (pygame.Surface): The current image of the player.
        rect (pygame.Rect): The rectangle defining the player's position and size.
        hitbox_rect (pygame.Rect): The rectangle defining the player's hitbox.
        direction (pygame.Vector2): The direction vector for player movement.
        speed (int): The speed of the player's movement.
        collision_sprites (pygame.sprite.Group): The group of sprites to check for collisions.
        health (int): The player's health.
        invulnerable (bool): A boolean indicating if the player is currently invulnerable.
        invulnerable_duration (int): The duration of the player's invulnerability after taking damage.
        last_hit_time (int): The time when the player was last hit.
        blink_duration (int): The duration for which the player blinks while invulnerable.
        last_blink_time (int): The time when the player last blinked.
        visible (bool): A boolean indicating if the player is currently visible.
    """

    def __init__(self, pos, groups, collision_sprites):
        """
        Initializes the Player object.

        Args:
            pos (tuple): The initial position of the player.
            groups (list): The groups that the player belongs to.
            collision_sprites (pygame.sprite.Group): The group of sprites to check for collisions.
        """
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = 'right', 0
        self.image = pygame.image.load(join('images', 'player', 'down', '0.png')).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-60, -90)
        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites
        self.health = 60

        self.invulnerable = False
        self.invulnerable_duration = 1500
        self.last_hit_time = 0
        self.blink_duration = 200
        self.last_blink_time = 0
        self.visible = True

    def decrease_health(self, amount):
        """
        Decreases the player's health by a specified amount and handles invulnerability and blinking.

        Args:
            amount (int): The amount of health to decrease.
        """
        if not self.invulnerable:
            if self.health != 20:
                hurt = pygame.mixer.Sound(join('audio', 'hurt.mp3'))
                hurt.play() 
                hurt.set_volume(0.2)
            self.health -= amount
            if self.health <= 0:
                self.health = 0
            else:
                self.invulnerable = True
                self.last_hit_time = pygame.time.get_ticks()
                self.last_blink_time = pygame.time.get_ticks()

    def load_images(self):
        """
        Loads the player's animation frames from the images folder.
        """
        self.frames = {'left': [], 'right': [], 'up': [], 'down': []}
        for state in self.frames.keys():
            for folder_path, _, file_names in walk(join('images', 'player', state)):
                for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.frames[state].append(surf)

    def input(self):
        """
        Handles player input and updates the direction vector based on key presses.
        """
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self, dt):
        """
        Moves the player and handles collisions.

        Args:
            dt (float): The delta time to ensure consistent movement speed.
        """
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        """
        Handles collisions with other sprites.

        Args:
            direction (str): The direction of movement ('horizontal' or 'vertical').
        """
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top

    def animate(self, dt):
        """
        Animates the player by updating the frame index based on the direction.

        Args:
            dt (float): The delta time to ensure consistent animation speed.
        """
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'
        self.frame_index = self.frame_index + 5 * dt if self.direction else 0
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def update(self, dt):
        """
        Updates the player's state.

        Args:
            dt (float): The delta time to ensure consistent updates.
        """
        self.input()
        self.move(dt)
        self.animate(dt)
        
        current_time = pygame.time.get_ticks()
        if self.invulnerable:
            if current_time - self.last_hit_time >= self.invulnerable_duration:
                self.invulnerable = False
                self.visible = True
                self.image.set_alpha(255)
            else:
                if current_time - self.last_blink_time >= self.blink_duration:
                    self.last_blink_time = current_time
                    self.visible = not self.visible
                    self.image.set_alpha(128 if not self.visible else 255)
        else:
            self.visible = True
            self.image.set_alpha(255)
