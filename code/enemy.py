from settings import *

class Enemy(pygame.sprite.Sprite):
    """
    A class representing an enemy sprite in the game.

    Attributes:
        pos (tuple): The initial position of the enemy.
        frames (list): List of images for the enemy animation.
        groups (list): List of sprite groups the enemy belongs to.
        player (pygame.sprite.Sprite): Reference to the player sprite for tracking.
        collision_sprites (pygame.sprite.Group): Sprites that the enemy can collide with.
        frame_index (int): The current frame index for animation.
        animation_speed (int): Speed at which the animation frames change.
        rect (pygame.Rect): Rectangle representing the enemy's position and size.
        hitbox_rect (pygame.Rect): Rectangle representing the enemy's collision box.
        direction (pygame.Vector2): Direction vector for the enemy's movement.
        speed (int): Movement speed of the enemy.
        death_time (int): Time when the enemy was destroyed.
        death_duration (int): Duration before the enemy is removed after destruction.
        hit (bool): Flag indicating if the enemy is hit.
        hit_duration (int): Duration the enemy remains in the hit state.
        hit_time (int): Time when the enemy was hit.
        invulnerable (bool): Flag indicating if the enemy is invulnerable to damage.
    """

    def __init__(self, pos, frames, groups, player, collision_sprites):
        """
        Initialize the enemy sprite.

        Args:
            pos (tuple): The initial position of the enemy.
            frames (list): List of images for the enemy animation.
            groups (list): List of sprite groups the enemy belongs to.
            player (pygame.sprite.Sprite): Reference to the player sprite for tracking.
            collision_sprites (pygame.sprite.Group): Sprites that the enemy can collide with.
        """
        super().__init__(groups)
        self.player = player
        self.frames, self.frame_index = frames, 0 
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6
        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-20, -40)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 200
        self.death_time = 0
        self.death_duration = 200
        self.hit = False
        self.hit_duration = 200  
        self.hit_time = 0
        self.invulnerable = False
    
    def animate(self, dt):
        """
        Animate the enemy sprite by updating its image.

        Args:
            dt (float): Delta time since the last frame.
        """
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def move(self, dt):
        """
        Move the enemy towards the player, handling collision with obstacles.

        Args:
            dt (float): Delta time since the last frame.
        """
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        """
        Handle collision detection and response.

        Args:
            direction (str): The direction of the movement ('horizontal' or 'vertical').
        """
        if not self.invulnerable:
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

    def destroy(self):
        """
        Handle the destruction of the enemy, setting its death time and changing its image.
        """
        self.death_time = pygame.time.get_ticks()
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf

    def death_timer(self):
        """
        Check if the enemy's death duration has passed and remove the sprite.
        """
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:   
            self.kill()

    def update(self, dt):
        """
        Update the enemy's state.

        Args:
            dt (float): Delta time since the last frame.
        """
        current_time = pygame.time.get_ticks()
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
            if self.hit and current_time - self.hit_time >= self.hit_duration:
                self.hit = False
                self.image = self.frames[int(self.frame_index) % len(self.frames)]
        else:
            self.death_timer()

    def take_damage(self):
        """
        Handle the enemy taking damage, making it invulnerable for a short duration.
        """
        if not self.invulnerable:
            self.hit = True
            self.hit_time = pygame.time.get_ticks()
            self.invulnerable = True
            pygame.time.set_timer(pygame.USEREVENT + 1, self.hit_duration)
            
            white_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            white_surface.fill((255, 255, 255, 0))  
            self.image = self.frames[int(self.frame_index) % len(self.frames)].copy()  

            white_image = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            white_image.fill((255, 255, 255))
            white_image.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            self.image.blit(white_image, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


