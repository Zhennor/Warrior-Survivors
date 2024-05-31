from settings import *


class Enemy(pygame.sprite.Sprite):
    """
    A class to represent an enemy in the game.

    Attributes:
        player (pygame.sprite.Sprite): The player sprite that the enemy will target.
        frames (list): List of surfaces for the enemy's animation frames.
        frame_index (int): The current frame index for animation.
        image (pygame.Surface): The current image of the enemy based on the frame index.
        animation_speed (int): Speed of the animation.
        rect (pygame.Rect): The rectangle representing the enemy's position.
        hitbox_rect (pygame.Rect): The hitbox of the enemy for collision detection.
        collision_sprites (pygame.sprite.Group): Group of sprites that the enemy can collide with.
        direction (pygame.Vector2): The direction vector of the enemy.
        speed (int): The speed of the enemy.
        death_time (int): The time when the enemy starts its death animation.
        death_duration (int): The duration of the death animation.
    """

    def __init__(self, pos, frames, groups, player, collision_sprites):
        """
        Initializes the Enemy object.

        Args:
            pos (tuple): The initial position of the enemy.
            frames (list): List of surfaces for the enemy's animation frames.
            groups (pygame.sprite.Group): Groups to which the enemy sprite belongs.
            player (pygame.sprite.Sprite): The player sprite that the enemy will target.
            collision_sprites (pygame.sprite.Group): Group of sprites that the enemy can collide with.
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

    def animate(self, dt):
        """
        Updates the animation frame of the enemy based on the time delta.

        Args:
            dt (float): The time delta between frames.
        """
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def move(self, dt):
        """
        Moves the enemy towards the player and handles collisions.

        Args:
            dt (float): The time delta between frames.
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
        Handles collision with other sprites in the specified direction.

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

    def destroy(self):
        """
        Destroys the enemy, starting the death animation.
        """
        self.death_time = pygame.time.get_ticks()
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf

    def death_timer(self):
        """
        Checks if the death animation duration has passed and removes the enemy sprite.
        """
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:   
            self.kill()

    def update(self, dt):
        """
        Updates the enemy each frame. Handles movement, animation, and death timer.

        Args:
            dt (float): The time delta between frames.
        """
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()

