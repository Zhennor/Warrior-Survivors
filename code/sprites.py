from settings import *
from math import atan2, degrees
import pygame

class Sprite(pygame.sprite.Sprite):
    """
    A basic sprite class that can be placed on the screen.

    Attributes:
        image (pygame.Surface): The surface representing the sprite's image.
        rect (pygame.Rect): The rectangle representing the sprite's position and size.
        ground (bool): A flag indicating if the sprite is on the ground.
    """
    
    def __init__(self, pos, surf, groups):
        """
        Initializes the Sprite object.

        Args:
            pos (tuple): The initial position of the sprite.
            surf (pygame.Surface): The surface representing the sprite's image.
            groups (list): The groups that the sprite belongs to.
        """
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.ground = True


class CollisionSprite(pygame.sprite.Sprite):
    """
    A sprite class specifically for handling collisions.

    Attributes:
        image (pygame.Surface): The surface representing the sprite's image.
        rect (pygame.Rect): The rectangle representing the sprite's position and size.
    """
    
    def __init__(self, pos, surf, groups):
        """
        Initializes the CollisionSprite object.

        Args:
            pos (tuple): The initial position of the sprite.
            surf (pygame.Surface): The surface representing the sprite's image.
            groups (list): The groups that the sprite belongs to.
        """
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)


class Bullet(pygame.sprite.Sprite):
    """
    A bullet sprite that moves in a given direction and has a limited lifetime.

    Attributes:
        image (pygame.Surface): The surface representing the bullet's image.
        rect (pygame.Rect): The rectangle representing the bullet's position and size.
        spawn_time (int): The time when the bullet was spawned.
        lifetime (int): The lifetime of the bullet in milliseconds.
        direction (pygame.Vector2): The direction vector of the bullet.
        speed (int): The speed of the bullet.
    """
    
    def __init__(self, surf, pos, direction, groups):
        """
        Initializes the Bullet object.

        Args:
            surf (pygame.Surface): The surface representing the bullet's image.
            pos (tuple): The initial position of the bullet.
            direction (pygame.Vector2): The direction vector of the bullet.
            groups (list): The groups that the bullet belongs to.
        """
        super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_rect(center=pos)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000
        self.direction = direction 
        self.speed = 1200 
    
    def update(self, dt):
        """
        Updates the bullet's position and checks if its lifetime has expired.

        Args:
            dt (float): The delta time to ensure consistent movement speed.
        """
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()
