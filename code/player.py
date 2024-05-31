import pygame
from os.path import join
from os import walk

WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE = 1280, 720, 64

class Player(pygame.sprite.Sprite):
    """
    A class to represent the player character in the game.

    Attributes:
        frames (dict): Dictionary containing lists of surfaces for each direction of player movement.
        state (str): The current direction state of the player ('left', 'right', 'up', 'down').
        frame_index (float): The current frame index for animation.
        image (pygame.Surface): The current image of the player.
        rect (pygame.Rect): The rectangle representing the position and size of the player sprite.
        hitbox_rect (pygame.Rect): The hitbox of the player for collision detection.
        direction (pygame.Vector2): The movement direction of the player.
        speed (int): The speed of the player's movement.
        collision_sprites (pygame.sprite.Group): Group of sprites that the player can collide with.
    """

    def __init__(self, pos, groups, collision_sprites):
        """
        Initializes the Player object.

        Args:
            pos (tuple): The initial position of the player.
            groups (pygame.sprite.Group): Groups to which the player sprite belongs.
            collision_sprites (pygame.sprite.Group): Group of sprites that the player can collide with.
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

    def load_images(self):
        """
        Loads player animation frames from image files.
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
        Moves the player based on input and handles collisions.

        Args:
            dt (float): The time delta between frames.
        """
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        """
        Handles collision detection and response with other sprites.

        Args:
            direction (str): The direction of movement ('horizontal' or 'vertical').
        """
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top

    def animate(self, dt):
        """
        Updates the player animation based on movement direction.

        Args:
            dt (float): The time delta between frames.
        """
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'
        self.frame_index = self.frame_index + 5 * dt if self.direction else 0
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def update(self, dt):
        """
        Updates the player sprite each frame.

        Args:
            dt (float): The time delta between frames.
        """
        self.input()
        self.move(dt)
        self.animate(dt)
