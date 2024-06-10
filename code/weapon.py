from settings import *
from math import atan2, degrees

class Weapon(pygame.sprite.Sprite):
    """
    A sprite class for weapons in the game.

    Attributes:
        player (Player): The player instance to which the weapon belongs.
        distance (int): The distance of the weapon from the player.
        player_direction (pygame.Vector2): The direction vector of the player's movement.
        gun_surf (pygame.Surface): The surface of the gun image.
        sword_surf (pygame.Surface): The surface of the sword image.
        image (pygame.Surface): The current image of the weapon.
        rect (pygame.Rect): The rectangle representing the weapon's position and size.
        weapon_type (str): The type of the weapon, either 'gun' or 'sword'.
    """

    def __init__(self, player, groups):
        """
        Initializes the Weapon.

        Args:
            player (Player): The player instance to which the weapon belongs.
            groups (list): The groups to which the weapon belongs.
        """
        super().__init__(groups)
        self.player = player
        self.distance = 140
        self.player_direction = pygame.Vector2(0, 1)
        self.gun_surf = pygame.image.load(join('images', 'weapon', 'gun.png')).convert_alpha()
        self.sword_surf = pygame.image.load(join('images', 'weapon', 'sword.png')).convert_alpha()
        self.image = self.gun_surf
        self.rect = self.image.get_rect(center=self.player.rect.center + self.player_direction * self.distance)
        self.weapon_type = 'gun'  

    def get_direction(self):
        """
        Calculates and updates the direction from the player to the mouse position.
        """
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()

    def switch_weapon(self):
        """
        Switches the weapon type between 'gun' and 'sword'.
        """
        if self.weapon_type == 'gun':
            self.weapon_type = 'sword'
            self.image = self.sword_surf
        else:
            self.weapon_type = 'gun'
            self.image = self.gun_surf

    def rotate_weapon(self):
        """
        Rotates the weapon image based on the player's direction.
        """
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.weapon_type == 'gun':
            if self.player_direction.x > 0:
                self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
            else:
                self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
                self.image = pygame.transform.flip(self.image, False, True)
        else:
            if self.player_direction.x > 0:
                self.image = pygame.transform.rotozoom(self.sword_surf, angle, 1)
            else:
                self.image = pygame.transform.rotozoom(self.sword_surf, abs(angle), 1)
                self.image = pygame.transform.flip(self.image, False, True)

    def update(self, _):
        """
        Updates the weapon's direction, rotation, and position.

        Args:
            _ (float): The time delta for the current frame, not used in this method.
        """
        self.get_direction()
        self.rotate_weapon()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance
