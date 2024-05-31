from settings import * 
from player import Player

class AllSprites(pygame.sprite.Group):
    """
    A custom sprite group that handles drawing sprites with an offset for a camera effect.

    Attributes:
        display_surface (pygame.Surface): The surface on which to draw the sprites.
        offset (pygame.Vector2): The offset used to adjust the sprite positions for the camera effect.
    """

    def __init__(self):
        """
        Initializes the AllSprites group.
        """
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target_pos):
        """
        Draws the sprites on the display surface with an offset based on the target position.

        Args:
            target_pos (tuple): The (x, y) position of the target to center the camera on.
        """
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'ground')] 
        object_sprites = [sprite for sprite in self if not hasattr(sprite, 'ground')] 
        for layer in [ground_sprites, object_sprites]:
            for sprite in sorted(layer, key = lambda sprite: sprite.rect.centery):
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
