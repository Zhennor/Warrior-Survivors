import pygame
from os.path import join
from settings import *
from math import atan2, degrees

class Weapon(pygame.sprite.Sprite):
    """
    Represents a weapon that the player can use.

    Attributes:
        player (Player): The player that wields the weapon.
        distance (int): The distance between the player and the weapon.
        player_direction (pygame.Vector2): The direction the player is facing.
        gun_surf (pygame.Surface): The image surface of the gun.
        image (pygame.Surface): The current image of the weapon.
        rect (pygame.Rect): The rectangle representing the weapon's position.
        weapon_type (str): The type of the weapon (default is 'gun').
    """

    def __init__(self, player, groups):
        """
        Initializes the Weapon object.

        Args:
            player (Player): The player that wields the weapon.
            groups (pygame.sprite.Group): The groups the weapon sprite belongs to.
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
        Calculates the direction from the player to the mouse cursor.
        """
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()

    def rotate_weapon(self):
        """
        Rotates the weapon image based on the player's direction.
        """
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self, _):
        """
        Updates the weapon's position and rotation.

        Args:
            _ (float): The delta time (not used in this method).
        """
        self.get_direction()
        self.rotate_weapon()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance
