from settings import *


class Enemy(pygame.sprite.Sprite):
    """
    The Enemy class represents an enemy character in the game.

    Attributes:
        player (Player): The player object to track and follow.
        frames (list): A list of images for the enemy's animation frames.
        frame_index (int): The current frame index for animation.
        image (pygame.Surface): The current image of the enemy.
        animation_speed (int): The speed of the enemy's animation.
        rect (pygame.Rect): The rectangle defining the enemy's position and size.
        hitbox_rect (pygame.Rect): The rectangle defining the enemy's hitbox.
        collision_sprites (pygame.sprite.Group): The group of sprites to check for collisions.
        direction (pygame.Vector2): The direction vector for enemy movement.
        speed (int): The speed of the enemy's movement.
        death_time (int): The time when the enemy started dying.
        death_duration (int): The duration of the enemy's death animation.
        hit (bool): A boolean indicating if the enemy is currently hit.
        hit_duration (int): The duration for which the enemy is in the hit state.
        hit_time (int): The time when the enemy was hit.
        invulnerable (bool): A boolean indicating if the enemy is currently invulnerable.
    """

    def __init__(self, pos, frames, groups, player, collision_sprites):
        """
        Initializes the Enemy object.

        Args:
            pos (tuple): The initial position of the enemy.
            frames (list): The list of animation frames for the enemy.
            groups (list): The groups that the enemy belongs to.
            player (Player): The player object to track and follow.
            collision_sprites (pygame.sprite.Group): The group of sprites to check for collisions.
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
        Animates the enemy by updating the frame index based on the animation speed.

        Args:
            dt (float): The delta time to ensure consistent animation speed.
        """
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def move(self, dt):
        """
        Moves the enemy towards the player.

        Args:
            dt (float): The delta time to ensure consistent movement speed.
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
        Handles collisions with other sprites.

        Args:
            direction (str): The direction of movement ('horizontal' or 'vertical').
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
        Prepares the enemy for destruction by setting the death time and updating the image.
        """
        self.death_time = pygame.time.get_ticks()
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf

    def death_timer(self):
        """
        Checks if the death duration has elapsed and destroys the enemy if so.
        """
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:   
            self.kill()

    def update(self, dt):
        """
        Updates the enemy's state.

        Args:
            dt (float): The delta time to ensure consistent updates.
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
        Handles the enemy taking damage by setting the hit state and updating the image.
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
