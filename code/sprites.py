from settings import *


class Sprite(pygame.sprite.Sprite):
    """
    A basic sprite class for objects in the game.

    Attributes:
        image (pygame.Surface): The surface of the sprite.
        rect (pygame.Rect): The rectangle representing the sprite's position and size.
        ground (bool): A flag to indicate if the sprite is a ground object.
    """

    def __init__(self, pos, surf, groups):
        """
        Initializes the Sprite.

        Args:
            pos (tuple): The position of the sprite.
            surf (pygame.Surface): The surface representing the sprite's image.
            groups (list): The groups to which the sprite belongs.
        """
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    """
    A sprite class for collision objects in the game.

    Attributes:
        image (pygame.Surface): The surface of the sprite.
        rect (pygame.Rect): The rectangle representing the sprite's position and size.
    """

    def __init__(self, pos, surf, groups):
        """
        Initializes the CollisionSprite.

        Args:
            pos (tuple): The position of the sprite.
            surf (pygame.Surface): The surface representing the sprite's image.
            groups (list): The groups to which the sprite belongs.
        """
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)

class Bullet(pygame.sprite.Sprite):
    """
    A sprite class for bullets in the game.

    Attributes:
        image (pygame.Surface): The surface of the bullet.
        rect (pygame.Rect): The rectangle representing the bullet's position and size.
        spawn_time (int): The time when the bullet was created.
        lifetime (int): The lifetime of the bullet in milliseconds.
        direction (pygame.Vector2): The direction vector of the bullet's movement.
        speed (int): The speed of the bullet.
    """

    def __init__(self, surf, pos, direction, groups):
        """
        Initializes the Bullet.

        Args:
            surf (pygame.Surface): The surface representing the bullet's image.
            pos (tuple): The position of the bullet.
            direction (pygame.Vector2): The direction of the bullet's movement.
            groups (list): The groups to which the bullet belongs.
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
        Updates the bullet's position and checks its lifetime.

        Args:
            dt (float): The time delta for the current frame.
        """
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()

