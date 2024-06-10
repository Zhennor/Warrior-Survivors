from sprites import Sprite, Bullet, Slash
from settings import *

class Player(pygame.sprite.Sprite):
    """
    A class representing the player in the game.

    Attributes:
        state (str): The current state of the player (e.g., 'right', 'left').
        frame_index (int): The current frame index for animation.
        image (pygame.Surface): The current image of the player.
        rect (pygame.Rect): The rectangular area of the player image.
        hitbox_rect (pygame.Rect): The hitbox rectangle for collision detection.
        direction (pygame.Vector2): The direction vector of the player's movement.
        speed (float): The speed of the player.
        collision_sprites (pygame.sprite.Group): The group of sprites for collision detection.
        health (int): The health of the player.
        invulnerable (bool): Whether the player is currently invulnerable.
        invulnerable_duration (int): The duration of invulnerability in milliseconds.
        last_hit_time (int): The time when the player was last hit.
        blink_duration (int): The duration of the blink effect in milliseconds.
        last_blink_time (int): The time when the player last blinked.
        visible (bool): Whether the player is currently visible.
        weapon (str): The current weapon of the player.
    """

    def __init__(self, pos, groups, collision_sprites):
        """
        Initializes the Player with the given position, groups, and collision sprites.

        Args:
            pos (tuple): The initial position of the player.
            groups (list): The groups to which the player belongs.
            collision_sprites (pygame.sprite.Group): The group of sprites for collision detection.
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
        self.weapon = 'gun'
            
    def decrease_health(self, amount):
        """
        Decreases the player's health by a given amount.

        Args:
            amount (int): The amount to decrease the player's health by.
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
        Loads the images for the player's animation frames.
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
        Handles player input for movement.
        """
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self, dt):
        """
        Moves the player based on the input direction and checks for collisions.

        Args:
            dt (float): The time delta for the current frame.
        """
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        """
        Handles collision detection and response.

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
        Updates the player's animation based on movement and direction.

        Args:
            dt (float): The time delta for the current frame.
        """
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'
        self.frame_index = self.frame_index + 5 * dt if self.direction else 0
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def update(self, dt):
        """
        Updates the player's state for the current frame.

        Args:
            dt (float): The time delta for the current frame.
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
