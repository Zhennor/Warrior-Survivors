from settings import *
from math import atan2, degrees

class Weapon(pygame.sprite.Sprite):
    """
    A class to represent a weapon attached to the player sprite.

    Attributes:
        player (pygame.sprite.Sprite): The player sprite to which the weapon is attached.
        distance (int): The distance of the weapon from the player sprite.
        player_direction (pygame.Vector2): The direction vector pointing from the player to the mouse cursor.
        gun_surf (pygame.Surface): The surface representing the weapon's image.
        image (pygame.Surface): The current image of the weapon.
        rect (pygame.Rect): The rectangle representing the position and size of the weapon.
        weapon_type (str): The type of weapon.
    """

    def __init__(self, player, groups):
        """
        Initializes the Weapon object.

        Args:
            player (pygame.sprite.Sprite): The player sprite to which the weapon is attached.
            groups (pygame.sprite.Group): Groups to which the weapon sprite belongs.
        """
        super().__init__(groups)
        self.player = player
        self.distance = 140
        self.player_direction = pygame.Vector2(0, 1)
        self.gun_surf = pygame.image.load(join('images', 'weapon', 'gun.png')).convert_alpha()
        self.image = self.gun_surf
        self.rect = self.image.get_rect(center=self.player.rect.center + self.player_direction * self.distance)
        self.weapon_type = 'gun'

    def get_direction(self):
        """
        Calculates the direction vector from the player to the mouse cursor.
        """
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()

    def rotate_weapon(self):
        """
        Rotates the weapon image based on the player direction.
        """
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self, _):
        """
        Updates the weapon sprite.

        Args:
            _ (any): Ignored argument. Required by the pygame.sprite.Sprite interface.
        """
        self.get_direction()
        self.rotate_weapon()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance
