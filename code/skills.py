from settings import *
from sprites import *

class PlayerSkills:
    """
    The PlayerSkills class handles the player's skills, including their usage and cooldowns.
    
    Attributes:
        game (Game): Reference to the game instance.
        skill_images (list): List of skill images.
        skill_positions (list): List of positions where skill icons are drawn.
        skill_cooldowns (list): List of cooldown durations for each skill.
        skill_last_used (list): List of timestamps when each skill was last used.
        gun_skill2_last_used_time (int): Timestamp when gun skill 2 was last used.
        sword_skill2_last_used_time (int): Timestamp when sword skill 2 was last used.
        skill_cooldown_alpha (int): Transparency level for skill cooldown overlay.
        skill2_active (bool): Indicates if skill 2 is active.
        skill2_cooldown_duration (int): Duration for which skill 2 remains active.
        slash_cooldown (int): Cooldown duration for the slash attack.
        last_slash_time (int): Timestamp when the last slash attack was performed.
        skill2_cooldown_time (int): Cooldown duration between consecutive skill 2 shots.
        last_skill2_shot_time (int): Timestamp when the last skill 2 shot was fired.
        count (int): Counter to manage alternating states.
        mouse_click_cooldown (int): Cooldown duration for mouse clicks.
        last_mouse_click_time (int): Timestamp when the last mouse click was registered.
    """

    def __init__(self, game):
        """Initializes the PlayerSkills object."""
        self.game = game
        self.skill_images = [
            pygame.image.load(join('images', 'skill', '0.jpg')).convert_alpha(),
            pygame.image.load(join('images', 'skill', '1.jpg')).convert_alpha(),
            pygame.image.load(join('images', 'skill', '2.jpg')).convert_alpha()
        ]
        self.skill_positions = [
            (WINDOW_WIDTH // 2 - 70, WINDOW_HEIGHT - 60),
            (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60),
            (WINDOW_WIDTH // 2 + 70, WINDOW_HEIGHT - 60)
        ]
        self.skill_cooldowns = [60000, 20000, 10000]
        self.skill_last_used = [pygame.time.get_ticks() - cooldown for cooldown in self.skill_cooldowns]

        self.gun_skill2_last_used_time = pygame.time.get_ticks() - self.skill_cooldowns[1]
        self.sword_skill2_last_used_time = pygame.time.get_ticks() - self.skill_cooldowns[1]
        self.skill_cooldown_alpha = 128
        self.skill2_active = False
        self.skill2_cooldown_duration = 5000
        self.slash_cooldown = 400
        self.last_slash_time = 0
        self.skill2_cooldown_time = 500
        self.last_skill2_shot_time = 0
        self.count = 0
        self.mouse_click_cooldown = 500  
        self.last_mouse_click_time = 0 

    def handle_skill_use(self, key):
        """
        Handles the use of skills based on key input.
        
        Args:
            key (int): The key pressed by the player.
        """
        current_time = pygame.time.get_ticks()
        skill_keys = [pygame.K_1, pygame.K_2, pygame.K_3]
        if key in skill_keys:
            skill_index = skill_keys.index(key)
            if skill_index == 1:
                if self.game.gun.weapon_type != 'sword' and current_time - self.gun_skill2_last_used_time >= self.skill_cooldowns[1]:
                    self.use_skill(skill_index)
                    self.gun_skill2_last_used_time = current_time
                elif self.game.gun.weapon_type == 'sword' and current_time - self.sword_skill2_last_used_time >= self.skill_cooldowns[1]:
                    self.use_skill(skill_index)
                    self.sword_skill2_last_used_time = current_time
            elif current_time - self.skill_last_used[skill_index] >= self.skill_cooldowns[skill_index]:
                self.use_skill(skill_index)
                self.skill_last_used[skill_index] = current_time

    def update_skills(self):
        """Updates the state of skills based on cooldowns."""
        current_time = pygame.time.get_ticks()
        if self.skill2_active and current_time - self.skill2_last_used_time >= self.skill2_cooldown_duration:
            self.skill2_active = False

    def perform_slash(self):
        """Performs a slash attack if the cooldown has elapsed."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_slash_time >= self.slash_cooldown:
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
            direction = (mouse_pos - player_pos).normalize()
            slash_pos = self.game.player.rect.center + direction * 100
            Slash(slash_pos, direction, (self.game.all_sprites, self.game.bullet_sprites))
            self.last_slash_time = current_time
            self.game.ui_ux.slash_sound.play()

    def use_skill(self, skill_index):
        """
        Uses a skill based on the skill index.
        
        Args:
            skill_index (int): The index of the skill to be used.
        """
        current_time = pygame.time.get_ticks()
        if skill_index == 0:
            self.game.ui_ux.health_heal_sound.play()
            self.game.player.health += 20
            if self.game.player.health > 60:
                self.game.player.health = 60
        elif skill_index == 1:
            if self.game.gun.weapon_type != 'sword' and not self.skill2_active:
                self.game.ui_ux.fireball_use_skill_sound.play()
                self.skill2_active = True
                self.skill2_last_used_time = current_time

                bullet_directions = [
                    self.game.gun.player_direction.rotate(angle)
                    for angle in range(-30, 31, 30)
                ]

                for direction in bullet_directions:
                    pos = self.game.gun.rect.center + direction * 50
                    Bullet(self.game.bullet_surf, pos, direction, (self.game.all_sprites, self.game.bullet_sprites))
            elif self.game.gun.weapon_type == 'sword':
                self.game.ui_ux.slash_use_skill_sound.play()
                directions = [pygame.Vector2(1, 0).rotate(angle) for angle in range(0, 360, 45)]
                for direction in directions:
                    slash_pos = self.game.player.rect.center + direction * 100
                    lifetime, speed = 300, 1000
                    Slash(slash_pos, direction, (self.game.all_sprites, self.game.bullet_sprites), lifetime, speed)
                    
        elif skill_index == 2:
            self.game.gun.switch_weapon()
            if self.count % 2 == 0:
                self.game.ui_ux.draw_sword_sound.play()
                self.skill_images[1] = pygame.image.load(join('images', 'skill', '4.jpg')).convert_alpha()
                self.skill_images[2] = pygame.image.load(join('images', 'skill', '5.jpg')).convert_alpha()
                self.count += 1
            else:
                self.game.ui_ux.fire_use_skill_sound.play()
                self.skill_images[1] = pygame.image.load(join('images', 'skill', '1.jpg')).convert_alpha()
                self.skill_images[2] = pygame.image.load(join('images', 'skill', '2.jpg')).convert_alpha()
                self.count += 1

    def handle_input(self):
        """Handles player input for shooting and slashing."""
        current_time = pygame.time.get_ticks()
        if pygame.mouse.get_pressed()[0]:
            if self.game.gun.weapon_type == 'sword':
                if current_time - self.last_mouse_click_time >= self.mouse_click_cooldown:
                    self.last_mouse_click_time = current_time
                    self.perform_slash()
            elif self.skill2_active:
                self.shoot_with_skill2()
            else:
                self.shoot_with_default_gun()

    def shoot_with_default_gun(self):
        """Shoots with the default gun if the cooldown has elapsed."""
        if self.game.can_shoot:
            self.game.ui_ux.shoot_sound.play()
            pos = self.game.gun.rect.center + self.game.gun.player_direction * 50
            Bullet(self.game.bullet_surf, pos, self.game.gun.player_direction, (self.game.all_sprites, self.game.bullet_sprites))
            self.game.can_shoot = False
            self.game.shoot_time = pygame.time.get_ticks()

    def shoot_with_skill2(self):
        """Shoots multiple bullets with skill 2 if the cooldown has elapsed."""
        current_time = pygame.time.get_ticks()
        if current_time - self.game.shoot_time >= self.game.gun_cooldown and current_time - self.last_skill2_shot_time >= self.skill2_cooldown_time:
            self.game.ui_ux.shoot_sound.play()
            bullet_directions = [
                self.game.gun.player_direction.rotate(angle)
                for angle in range(-30, 31, 30)
            ]
            for direction in bullet_directions:
                pos = self.game.gun.rect.center + direction * 50
                Bullet(self.game.bullet_surf, pos, direction, (self.game.all_sprites, self.game.bullet_sprites))
            self.game.can_shoot = False
            self.game.shoot_time = current_time
            self.last_skill2_shot_time = current_time

    def reset_skills(self):
        """Resets the state of the player's skills for new game."""
        current_time = pygame.time.get_ticks()
        self.skill_last_used = [current_time - cooldown for cooldown in self.skill_cooldowns]
        self.gun_skill2_last_used_time = current_time - self.skill_cooldowns[1]
        self.sword_skill2_last_used_time = current_time - self.skill_cooldowns[1]
        self.skill2_active = False
        self.count = 0
        self.skill_images = [
            pygame.image.load(join('images', 'skill', '0.jpg')).convert_alpha(),
            pygame.image.load(join('images', 'skill', '1.jpg')).convert_alpha(),
            pygame.image.load(join('images', 'skill', '2.jpg')).convert_alpha()
        ]
        self.last_slash_time = 0
        self.last_skill2_shot_time = 0
        self.last_mouse_click_time = 0
