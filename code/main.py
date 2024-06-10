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
from skills import PlayerSkills  

class Game:
    """
    The Game class represents the main game loop and handles game states, events, and updates.

    Attributes:
        display_surface (Surface): The main display surface.
        clock (Clock): The game clock for managing frame rate.
        running (bool): Flag to indicate if the game is running.
        menu_options (list): List of menu options.
        menu (Menu): The menu object.
        ui_ux (UI): The UI/UX handler object.
        all_sprites (AllSprites): Group containing all sprites.
        collision_sprites (Group): Group containing collision sprites.
        bullet_sprites (Group): Group containing bullet sprites.
        enemy_sprites (Group): Group containing enemy sprites.
        can_shoot (bool): Flag indicating if the player can shoot.
        shoot_time (int): Timestamp of the last shot.
        gun_cooldown (int): Cooldown duration for the gun.
        enemy_event (int): Custom event type for spawning enemies.
        spawn_positions (list): List of possible spawn positions for enemies.
        max_enemies (int): Maximum number of enemies allowed on the screen.
        bullet_surf (Surface): Surface for bullet images.
        enemy_frames (dict): Dictionary mapping enemy types to their animation frames.
        score (int): Player's score.
        state (str): Current game state ('menu', 'guide', 'game', 'game_over').
        guide_text (list): List of guide text lines.
        player_skills (PlayerSkills): The PlayerSkills object for managing player skills.
    """

    def __init__(self):
        """Initializes the Game object."""
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
        self.state = 'menu'
        self.guide_text = [
            "Welcome to Survivor!",
            "Use WASD or arrow keys to move.",
            "Use 1 2 3 for skill.",
            "Click to shoot or slash.",
            "Avoid enemies and try to survive as long as possible.",
            "Good luck!",
            "Press ESC to quit."
        ]

        self.player_skills = PlayerSkills(self) 

    def load_images(self):
        """Loads images for bullets and enemies."""
        self.bullet_surf = pygame.image.load(join('images', 'weapon', 'bullet.png')).convert_alpha()
        folders = list(walk(join('images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
                self.enemy_frames[folder] = [pygame.image.load(join(folder_path, file_name)).convert_alpha() for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0]))]
    
    def update_skills(self):
        """Updates the state of skills based on cooldowns."""
        self.player_skills.update_skills()

    def input(self):
        """Handles player input for shooting and slashing."""
        self.player_skills.handle_input()

    def gun_timer(self):
        """Resets the shooting ability if the cooldown has elapsed."""
        if not self.can_shoot:
            if pygame.time.get_ticks() - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def setup(self):
        """Sets up the game by loading the map and placing objects."""
        map = load_pygame(join('data', 'maps', 'world.tmx'))

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        for obj in map.get_layer_by_name('Entities'):
            if (obj.name == 'Player'):
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Weapon(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y)) 

    def bullet_slash_collision(self):
        """Handles collision detection between bullets/slash and enemies."""
        for bullet in self.bullet_sprites:
            collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if collision_sprites:
                if self.gun.weapon_type == 'gun':
                    self.ui_ux.impact_sound.play()
                else: 
                    self.ui_ux.blood_sound.play()
                for enemy in collision_sprites:
                    if not enemy.hit:
                        enemy.take_damage()
                        enemy.destroy()
                        self.score += 10
                    else:
                        enemy.take_damage()
                bullet.kill()

    def player_collision(self):
        """Handles collision detection between the player and enemies."""
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

    def reset_game(self):
        """Resets the game state to start a new game."""
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
        self.player_skills.reset_skills()

    def run(self):
        """Runs the main game loop."""
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
                        self.player_skills.handle_skill_use(event.key)
                self.gun_timer()
                self.input()
                self.all_sprites.update(dt)
                self.bullet_slash_collision()
                self.player_collision()
                self.update_skills()
                self.display_surface.fill('black')
                self.all_sprites.draw(self.player.rect.center)
                self.ui_ux.draw_score(self.score)
                self.ui_ux.draw_health_bar(self.player.health)
                self.ui_ux.draw_skills(self.player_skills.skill_images, self.player_skills.skill_positions, self.player_skills.skill_cooldowns, self.player_skills.skill_last_used, self.player_skills.gun_skill2_last_used_time, self.player_skills.sword_skill2_last_used_time, self.player_skills.skill_cooldown_alpha, self.player_skills.skill2_active, self.gun.weapon_type, self.all_sprites, self.bullet_sprites)
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
        """Spawns a new enemy if the number of enemies is below the maximum."""
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