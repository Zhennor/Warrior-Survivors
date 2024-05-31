from pygame.locals import *
from random import choice
from pytmx.util_pygame import load_pygame
from settings import *
from sprites import *
from groups import AllSprites
from player import Player
from weapon import Weapon
from enemy import Enemy
from ui import Menu

class Game:
    """
    A class to represent the game 'Warrior Survivors'.

    Attributes:
    -----------
    display_surface : pygame.Surface
        The main display surface for the game.
    clock : pygame.time.Clock
        The game clock to manage the frame rate.
    running : bool
        Flag to keep the main game loop running.
    menu_options : list of str
        List of options for the game menu.
    menu : Menu
        The game menu instance.
    font : pygame.font.Font
        Font for rendering text in the game.
    all_sprites : AllSprites
        Group containing all game sprites.
    collision_sprites : pygame.sprite.Group
        Group containing sprites that can collide.
    bullet_sprites : pygame.sprite.Group
        Group containing bullet sprites.
    enemy_sprites : pygame.sprite.Group
        Group containing enemy sprites.
    can_shoot : bool
        Flag to control shooting ability.
    shoot_time : int
        Timestamp for the last shot fired.
    gun_cooldown : int
        Cooldown time for the gun in milliseconds.
    enemy_event : int
        Custom event for spawning enemies.
    spawn_positions : list of tuple
        List of valid enemy spawn positions.
    max_enemies : int
        Maximum number of enemies allowed on screen.
    bullet_surf : pygame.Surface
        Surface for bullet image.
    enemy_frames : dict
        Dictionary holding enemy animation frames.
    player : Player
        The player character.
    gun : Weapon
        The player's weapon.
    state : str
        The current state of the game ('menu', 'guide', 'game', 'game_over').
    guide_text : list of str
        Text instructions for the guide screen.
    """

    def __init__(self):
        """
        Initializes the game, sets up display, clock, and game state, 
        and loads necessary resources.
        """
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Warrior Survivors')
        self.clock = pygame.time.Clock()
        self.running = True

        self.menu_options = ["Start", "Guide", "Exit"]
        self.menu = Menu(self.menu_options)
        self.font = pygame.font.Font(None, 36)
        
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

    def load_images(self):
        """
        Loads images for bullets and enemies from the filesystem.
        """
        self.bullet_surf = pygame.image.load(join('images', 'weapon', 'bullet.png')).convert_alpha()
        folders = list(walk(join('images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
                self.enemy_frames[folder] = [pygame.image.load(join(folder_path, file_name)).convert_alpha() for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0]))]
                
    def setup(self):
        """
        Sets up the game map, player, and initial positions for spawning enemies.
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

    def input(self):
        """
        Handles player input for shooting.
        """
        if pygame.mouse.get_pressed()[0]:
            self.shoot_with_default_gun()

    def shoot_with_default_gun(self):
        """
        Handles shooting logic, creates bullet instances, and sets cooldown.
        """
        if self.can_shoot:
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        """
        Manages the gun's cooldown timer.
        """
        if not self.can_shoot:
            if pygame.time.get_ticks() - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True
                
    def bullet_collision(self):
        """
        Checks for collisions between bullets and enemies.
        """
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    for sprite in collision_sprites:
                        sprite.destroy()
                    bullet.kill()
                    
    def player_collision(self):
        """
        Checks for collisions between the player and enemies.
        """
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.running = False
            
    def update(self):
        """
        Updates the game state, processes events, handles input, and draws the frame.
        """
        dt = self.clock.tick() / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == self.enemy_event:
                self.spawn_enemy()

        self.gun_timer()
        self.input()
        self.all_sprites.update(dt)
        self.bullet_collision()
        self.player_collision()
        self.display_surface.fill('black')
        self.all_sprites.draw(self.player.rect.center)
        pygame.display.update()

    def spawn_enemy(self):
        """
        Spawns an enemy at a random valid position.
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

    def run(self):
        """
        Runs the main game loop, managing different game states.
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
                self.draw_guide()

            elif self.state == 'game':
                self.update()
                
            elif self.state == 'game_over':
                self.draw_game_over_screen()
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.reset_game()

        pygame.quit()

    def draw_guide(self):
        """
        Draws the game guide on the screen.
        """
        self.display_surface.fill('black')
        guide_bg = pygame.image.load(join('images', 'back_ground', 'guide.png')).convert_alpha()
        self.display_surface.blit(guide_bg, (0, 0))
        survival_guide_img = pygame.image.load(join('images', 'back_ground', 'guidebook.png')).convert_alpha()
        self.display_surface.blit(survival_guide_img, (10, 10))  
        for i, line in enumerate(self.guide_text):
            text_surf = self.font.render(line, True, 'white')
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100 + i * 40))
            self.display_surface.blit(text_surf, text_rect)
        pygame.display.update()

    def draw_game_over_screen(self):
        """
        Draws the game over screen.
        """
        self.display_surface.fill('black')
        game_over_surf = pygame.font.Font(None, 80).render("Game Over", True, 'white')
        game_over_rect = game_over_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.display_surface.blit(game_over_surf, game_over_rect)

        pygame.display.update()

    def reset_game(self):
        """
        Resets the game state to the initial setup.
        """
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.can_shoot = True
        self.shoot_time = 0
        self.state = 'menu'
        self.load_images()
        self.setup()

if __name__ == '__main__':
    game = Game()
    game.run()
