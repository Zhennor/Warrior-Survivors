import pygame
from pygame.locals import *
from random import choice
from pytmx.util_pygame import load_pygame
from settings import *
from sprites import *
from groups import AllSprites
from player import Player
from weapon import Weapon
from enemy import Enemy
from ui import UI, Menu

class Game:
    def __init__(self):
        """
        Initialize the game, setting up the display, clock, and initial game state.
        Load images, setup the map, and configure initial settings for skills, player, and enemy spawns.

        Attributes:
        - display_surface (pygame.Surface): The main display surface for the game.
        - clock (pygame.time.Clock): The clock object to control game frame rate.
        - running (bool): Flag to determine if the game is running.
        - menu_options (list): List of menu options.
        - menu (Menu): Menu object for handling the game menu.
        - ui_ux (UI): UI object for handling game UI elements.
        - all_sprites (AllSprites): Group containing all the game sprites.
        - collision_sprites (pygame.sprite.Group): Group containing collision sprites.
        - bullet_sprites (pygame.sprite.Group): Group containing bullet sprites.
        - enemy_sprites (pygame.sprite.Group): Group containing enemy sprites.
        - can_shoot (bool): Flag to determine if the player can shoot.
        - shoot_time (int): Time when the player last shot.
        - gun_cooldown (int): Cooldown time for shooting in milliseconds.
        - enemy_event (int): Custom event type for spawning enemies.
        - spawn_positions (list): List of possible enemy spawn positions.
        - max_enemies (int): Maximum number of enemies allowed on screen.
        - score (int): Player's current score.
        - count (int): Counter for various purposes.
        - state (str): Current state of the game ('menu', 'guide', 'game', 'game_over').
        - guide_text (list): List of guide text strings for the guide screen.
        - skill_images (list): List of skill images.
        - skill_positions (list): List of skill icon positions.
        - skill_cooldowns (list): List of skill cooldown times in milliseconds.
        - skill_last_used (list): List of times when each skill was last used.
        - gun_skill2_last_used_time (int): Time when skill 2 was last used.
        - skill_cooldown_alpha (int): Alpha value for skill cooldown overlay.
        - skill2_active (bool): Flag to determine if skill 2 is active.
        - skill2_cooldown_duration (int): Duration for skill 2 effect in milliseconds.
        """
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Warrior Survivors')
        self.clock = pygame.time.Clock()
        self.running = True

        self.menu_options = ["Start", "Guide", "Exit"]
        self.menu = Menu(self.menu_options)
        self.ui_ux = UI(self.display_surface, pygame.font.Font(None, 36))

        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 100

        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []
        self.max_enemies = 20

        self.load_images()
        self.setup()

        self.score = 0
        self.count = 0
        self.state = 'menu'
        self.guide_text = [
            "Welcome to Survivor!",
            "Use WASD or arrow keys to move.",
            "Use 1 2 for skill.",
            "Click to shoot.",
            "Avoid enemies and try to survive as long as possible.",
            "Good luck!",
            "Press ESC to quit."
        ]
        self.skill_images = [
            pygame.image.load(join('images', 'skill', '0.jpg')).convert_alpha(),
            pygame.image.load(join('images', 'skill', '1.jpg')).convert_alpha()
        ]

        self.skill_positions = [
            (WINDOW_WIDTH // 2 - 70, WINDOW_HEIGHT - 60),
            (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60)
        ]

        self.skill_cooldowns = [60000, 20000]
        self.skill_last_used = [pygame.time.get_ticks() - cooldown for cooldown in self.skill_cooldowns]

        self.gun_skill2_last_used_time = pygame.time.get_ticks() - self.skill_cooldowns[1]
        self.skill_cooldown_alpha = 128
        self.skill2_active = False
        self.skill2_cooldown_duration = 5000

    def handle_skill_use(self, key):
        """
        Handle the use of skills based on the key pressed.
        
        Args:
        - key (int): The key pressed by the player.
        """
        current_time = pygame.time.get_ticks()
        skill_keys = [pygame.K_1, pygame.K_2]
        if key in skill_keys:
            skill_index = skill_keys.index(key)
            if skill_index == 1:
                if current_time - self.gun_skill2_last_used_time >= self.skill_cooldowns[1]:
                    self.use_skill(skill_index)
                    self.gun_skill2_last_used_time = current_time
            elif current_time - self.skill_last_used[skill_index] >= self.skill_cooldowns[skill_index]:
                self.use_skill(skill_index)
                self.skill_last_used[skill_index] = current_time

    def load_images(self):
        """
        Load images for bullets and enemies.
        """
        self.bullet_surf = pygame.image.load(join('images', 'weapon', 'bullet.png')).convert_alpha()
        folders = list(walk(join('images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
                self.enemy_frames[folder] = [pygame.image.load(join(folder_path, file_name)).convert_alpha() for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0]))]

    def update_skills(self):
        """
        Update the state of the skills, checking for cooldowns and activation duration.
        """
        current_time = pygame.time.get_ticks()
        if self.skill2_active and current_time - self.skill2_last_used_time >= self.skill2_cooldown_duration:
            self.skill2_active = False

    def use_skill(self, skill_index):
        """
        Use the specified skill.
        
        Args:
        - skill_index (int): The index of the skill to be used.
        """
        current_time = pygame.time.get_ticks()
        if skill_index == 0:
            self.ui_ux.health_heal_sound.play()
            self.player.health += 20
            if self.player.health > 60:
                self.player.health = 60
        elif skill_index == 1:
            if not self.skill2_active:
                self.ui_ux.fireball_use_skill_sound.play()
                self.skill2_active = True
                self.skill2_last_used_time = current_time

                bullet_directions = [
                    self.gun.player_direction.rotate(angle)
                    for angle in range(-30, 31, 30)
                ]

                for direction in bullet_directions:
                    pos = self.gun.rect.center + direction * 50
                    Bullet(self.bullet_surf, pos, direction, (self.all_sprites, self.bullet_sprites))

    def reset_game(self):
        """
        Reset the game to its initial state, clearing all sprites and resetting attributes.
        """
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.can_shoot = True
        self.shoot_time = 0
        self.ui_ux.music.play(loops=-1)
        self.score = 0
        self.player.health = 60
        self.state = 'menu'
        self.load_images()
        self.setup()
        self.count = 0
        self.skill_images = [
            pygame.image.load(join('images', 'skill', '0.jpg')).convert_alpha(),
            pygame.image.load(join('images', 'skill', '1.jpg')).convert_alpha()
        ]

        current_time = pygame.time.get_ticks()
        self.skill_last_used = [current_time - cooldown for cooldown in self.skill_cooldowns]
        self.gun_skill2_last_used_time = current_time - self.skill_cooldowns[1]
        self.skill2_active = False

    def input(self):
        """
        Handle the player's input for shooting.
        """
        if pygame.mouse.get_pressed()[0]:
            if self.skill2_active:
                self.shoot_with_skill2()
            else:
                self.shoot_with_default_gun()

    def shoot_with_default_gun(self):
        """
        Shoot with the default gun if the player can shoot.
        """
        if self.can_shoot:
            self.ui_ux.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def shoot_with_skill2(self):
        """
        Shoot with skill 2 if it is active.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.shoot_time >= self.gun_cooldown:
            self.ui_ux.shoot_sound.play()
            bullet_directions = [
                self.gun.player_direction.rotate(angle)
                for angle in range(-30, 31, 30)
            ]
            for direction in bullet_directions:
                pos = self.gun.rect.center + direction * 50
                Bullet(self.bullet_surf, pos, direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = current_time

    def gun_timer(self):
        """
        Handle the cooldown timer for the gun.
        """
        if not self.can_shoot:
            if pygame.time.get_ticks() - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def setup(self):
        """
        Setup the game map, player, and initial enemy spawn positions.
        """
        map = load_pygame(join('data', 'maps', 'world.tmx'))

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Weapon(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def bullet_collision(self):
        """
        Handle bullet collisions with enemies.
        """
        for bullet in self.bullet_sprites:
            collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if collision_sprites:
                self.ui_ux.impact_sound.play()
                for enemy in collision_sprites:
                    if not enemy.hit:
                        enemy.take_damage()
                        enemy.destroy()
                        self.score += 10
                    else:
                        enemy.take_damage()
                bullet.kill()

    def player_collision(self):
        """
        Handle collisions between the player and enemies.
        """
        colliding_enemies = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
        if colliding_enemies:
            for enemy in colliding_enemies:
                if not enemy.invulnerable:
                    enemy.take_damage()
                    enemy.destroy()
                    self.player.decrease_health(20)
                    if self.player.health == 0:
                        self.state = 'game_over'
                        self.ui_ux.game_over_sound.play()

    def run(self):
        """
        Run the main game loop, handling state transitions and game logic.
        """
        while self.running:
            if self.state == 'menu':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    selected_option = self.menu.handle_input(event)
                    if selected_option is not None:
                        if selected_option == 0:
                            self.state = 'game'
                        elif selected_option == 1:
                            self.state = 'guide'
                        elif selected_option == 2:
                            self.running = False
                self.display_surface.fill('black')
                self.menu.draw(self.display_surface)
                pygame.display.update()

            elif self.state == 'guide':
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                self.ui_ux.draw_guide(self.guide_text)

            elif self.state == 'game':
                dt = self.clock.tick() / 1000
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == self.enemy_event:
                        self.spawn_enemy()
                    if event.type == pygame.KEYDOWN:
                        self.handle_skill_use(event.key)
                self.gun_timer()
                self.input()
                self.all_sprites.update(dt)
                self.bullet_collision()
                self.player_collision()
                self.update_skills()
                self.display_surface.fill('black')
                self.all_sprites.draw(self.player.rect.center)
                self.ui_ux.draw_score(self.score)
                self.ui_ux.draw_health_bar(self.player.health)
                self.ui_ux.draw_skills(self.skill_images, self.skill_positions, self.skill_cooldowns, self.skill_last_used, self.gun_skill2_last_used_time, self.skill_cooldown_alpha, self.skill2_active, self.gun.weapon_type, self.all_sprites, self.bullet_sprites)
                pygame.display.update()

            elif self.state == 'game_over':
                self.ui_ux.draw_game_over_screen(self.score)
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.reset_game()

        pygame.quit()

    def spawn_enemy(self):
        """
        Spawn a new enemy at a random valid spawn position.
        """
        if len(self.enemy_sprites) < self.max_enemies:
            valid_spawn = False
            while not valid_spawn:
                spawn_pos = choice(self.spawn_positions)
                player_pos = pygame.Vector2(self.player.rect.center)
                valid_spawn = True

                for sprite in self.collision_sprites:
                    if (sprite.rect.left <= spawn_pos[0] <= sprite.rect.right) and \
                    (sprite.rect.top <= spawn_pos[1] <= sprite.rect.bottom):
                        valid_spawn = False
                        break

                if valid_spawn and pygame.Vector2(spawn_pos).distance_to(player_pos) < 400:
                    valid_spawn = False

            if valid_spawn:
                Enemy(spawn_pos, choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)

if __name__ == '__main__':
    game = Game()
    game.run()
