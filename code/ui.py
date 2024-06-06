import pygame
from os.path import join
from settings import *

class Menu:
    """
    Represents the main menu of the game with selectable options.

    Attributes:
        options (list): List of menu options.
        selected_option (int): Index of the currently selected option.
        background (pygame.Surface): Background image of the menu.
        button_image (pygame.Surface): Image used for the buttons.
        button_rects (list): List of rectangles representing the button positions.
    """
    
    def __init__(self, options):
        """
        Initializes the Menu object.

        Args:
            options (list): List of options to be displayed in the menu.
        """
        self.options = options
        self.selected_option = None
        self.background = pygame.image.load(join('images', 'back_ground', 'bg.jpg')).convert_alpha()
        self.button_image = pygame.image.load(join('images', 'back_ground', 'button.png')).convert_alpha()
        self.button_rects = []

    def draw(self, surface):
        """
        Draws the menu on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the menu on.
        """
        surface.blit(self.background, (0, 0))
        menu_font = pygame.font.Font(None, 40)
        title_font = pygame.font.Font(None, 80)
        title_surf = title_font.render("WARRIOR SURVIVORS", True, 'black')
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        surface.blit(title_surf, title_rect)

        button_width, button_height = self.button_image.get_size()
        button_y = WINDOW_HEIGHT // 2

        self.button_rects = []
        for i in range(3):
            button_x = (WINDOW_WIDTH - button_width) // 2
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            self.button_rects.append(button_rect)
            surface.blit(self.button_image, button_rect.topleft)
            button_y += button_height + 20

        for i, option in enumerate(self.options):
            text_color = 'white'
            text_surf = menu_font.render(option, True, text_color)
            text_rect = text_surf.get_rect(center=self.button_rects[i].center)
            surface.blit(text_surf, text_rect)

    def handle_input(self, event):
        """
        Handles user input for selecting menu options.

        Args:
            event (pygame.event.Event): The event to handle.

        Returns:
            int or None: The index of the selected option, or None if no option is selected.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, button_rect in enumerate(self.button_rects):
                if button_rect.collidepoint(mouse_pos):
                    self.selected_option = i
                    return self.selected_option
        return None


class UI:
    """
    Represents the game's user interface, including sounds, health bar, score, and other elements.

    Attributes:
        display_surface (pygame.Surface): The surface to draw the UI on.
        font (pygame.font.Font): The font used for text in the UI.
    """
    
    def __init__(self, display_surface, font):
        """
        Initializes the UI object.

        Args:
            display_surface (pygame.Surface): The surface to draw the UI on.
            font (pygame.font.Font): The font used for text in the UI.
        """
        self.display_surface = display_surface
        self.font = font
        self.load_sounds()

    def load_sounds(self):
        """
        Loads the sound effects and background music for the game.
        """
        self.shoot_sound = pygame.mixer.Sound(join('audio', 'fireball.mp3'))
        self.shoot_sound.set_volume(0.2)
        self.impact_sound = pygame.mixer.Sound(join('audio', 'impact.mp3'))
        self.impact_sound.set_volume(1)
        self.music = pygame.mixer.Sound(join('audio', 'music.mp3'))
        self.music.set_volume(0.2)
        self.music.play(loops=-1)
        self.game_over_sound = pygame.mixer.Sound(join('audio', 'game_over.mp3'))
        self.game_over_sound.set_volume(0.2)
        self.health_heal_sound = pygame.mixer.Sound(join('audio', 'health_heal.mp3'))
        self.health_heal_sound.set_volume(0.5)
        self.fireball_use_skill_sound = pygame.mixer.Sound(join('audio', 'fireball_use_skill.mp3'))
        self.fireball_use_skill_sound.set_volume(0.2)

    def draw_health_bar(self, health):
        """
        Draws the health bar on the screen.

        Args:
            health (int): The current health of the player.
        """
        bar_width, bar_height = 200, 20
        health_bar_color = (255, 0, 0)
        background_bar_color = (128, 128, 128)
        health_width = (health / 60) * bar_width
        health_rect = pygame.Rect(10, 50, health_width, bar_height)
        background_rect = pygame.Rect(10, 50, bar_width, bar_height)
        pygame.draw.rect(self.display_surface, background_bar_color, background_rect)
        pygame.draw.rect(self.display_surface, health_bar_color, health_rect)
        health_text = self.font.render(f'{health}/60', True, 'black')
        self.display_surface.blit(health_text, (10, 50))

    def draw_score(self, score):
        """
        Draws the score on the screen.

        Args:
            score (int): The current score of the player.
        """
        score_surf = self.font.render(f'Score: {score}', True, 'black')
        self.display_surface.blit(score_surf, (10, 10))

    def draw_game_over_screen(self, score):
        """
        Draws the game over screen.

        Args:
            score (int): The final score of the player.
        """
        self.music.stop()
        game_over_bg = pygame.image.load(join('images', 'back_ground', 'bg_over.jpg')).convert_alpha()
        self.display_surface.blit(game_over_bg, (0, 0))
        score_font = pygame.font.Font(None, 60)
        score_surf = score_font.render(f"Final Score: {score}", True, 'white')
        score_rect = score_surf.get_rect(midbottom=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 90))
        self.display_surface.blit(score_surf, score_rect)
        esc_font = pygame.font.Font(None, 39)
        esc_surf = esc_font.render("Press ESC to return to menu", True, 'white')
        esc_rect = esc_surf.get_rect(midtop=(WINDOW_WIDTH // 2, score_rect.bottom + 41))
        self.display_surface.blit(esc_surf, esc_rect)

    def draw_guide(self, guide_text):
        """
        Draws the game guide on the screen.

        Args:
            guide_text (list): List of strings representing the guide text.
        """
        self.display_surface.fill('black')
        guide_bg = pygame.image.load(join('images', 'back_ground', 'guide.png')).convert_alpha()
        self.display_surface.blit(guide_bg, (0, 0))
        survival_guide_img = pygame.image.load(join('images', 'back_ground', 'guidebook.png')).convert_alpha()
        self.display_surface.blit(survival_guide_img, (10, 10))  
        for i, line in enumerate(guide_text):
            text_surf = self.font.render(line, True, 'white')
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100 + i * 40))
            self.display_surface.blit(text_surf, text_rect)
        pygame.display.update()

    def draw_skills(self, skill_images, skill_positions, skill_cooldowns, skill_last_used, gun_skill2_last_used_time, skill_cooldown_alpha, skill2_active, player_direction, all_sprites, bullet_sprites):
        """
        Draws the skill icons and their cooldowns on the screen.

        Args:
            skill_images (list): List of skill icon images.
            skill_positions (list): List of positions for the skill icons.
            skill_cooldowns (list): List of cooldown times for each skill.
            skill_last_used (list): List of timestamps for when each skill was last used.
            gun_skill2_last_used_time (int): The last used time for the second gun skill.
            skill_cooldown_alpha (int): The alpha value for the skill cooldown overlay.
            skill2_active (bool): Flag indicating if the second skill is active.
            player_direction (pygame.Vector2): The direction the player is facing.
            all_sprites (pygame.sprite.Group): Group containing all sprites.
            bullet_sprites (pygame.sprite.Group): Group containing bullet sprites.
        """
        current_time = pygame.time.get_ticks()
        for i, (image, cooldown) in enumerate(zip(skill_images, skill_cooldowns)):
            if i == 1:
                cooldown_remaining = max(0, cooldown - (current_time - gun_skill2_last_used_time))
            else:
                cooldown_remaining = max(0, cooldown - (current_time - skill_last_used[i]))
            
            alpha = skill_cooldown_alpha if cooldown_remaining > 0 else 255
            image.set_alpha(alpha)
            if cooldown_remaining > 0:
                font = pygame.font.Font(None, 24)
                cooldown_text = font.render(f"{cooldown_remaining // 1000}", True, (255, 255, 255))
                self.display_surface.blit(image, skill_positions[i])
                text_rect = cooldown_text.get_rect(center=(skill_positions[i][0] + 30, skill_positions[i][1] + 30))
                self.display_surface.blit(cooldown_text, text_rect)
            else:
                self.display_surface.blit(image, skill_positions[i])
            font = pygame.font.Font(None, 24)
            number_text = font.render(str(i + 1), True, (255, 255, 255))
            self.display_surface.blit(number_text, (skill_positions[i][0], skill_positions[i][1]))
            skill_rect = pygame.Rect(skill_positions[i][0], skill_positions[i][1], image.get_width(), image.get_height())
            pygame.draw.rect(self.display_surface, (255, 255, 255), skill_rect, 2)
