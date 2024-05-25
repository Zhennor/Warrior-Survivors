from settings import *

class Menu:
    """
    A class representing the game menu.

    Attributes:
        options (list): A list of menu options.
        selected_option (int or None): The index of the selected menu option, or None if no option is selected.
        background (pygame.Surface): The background image for the menu.
    """

    def __init__(self, options):
        """
        Initializes the Menu with a list of options.

        Args:
            options (list): A list of menu options.
        """
        self.options = options
        self.selected_option = None
        self.background = pygame.image.load(join('images', 'back_ground', 'bg.jpg')).convert_alpha()
        self.button_image = pygame.image.load(join('images', 'back_ground', 'button.png')).convert_alpha()

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
        
        # Draw buttons
        button_width, button_height = self.button_image.get_size()
        button_y = WINDOW_HEIGHT // 2
        for i in range(3):
            button_x = (WINDOW_WIDTH - button_width) // 2
            surface.blit(self.button_image, (button_x, button_y))
            button_y += button_height + 20  # Increase vertical space between buttons
        
        # Draw menu options
        self.option_rects = []
        for i, option in enumerate(self.options):
            text_color = 'white'
            text_surf = menu_font.render(option, True, text_color)
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, (WINDOW_HEIGHT // 2) + (i * (button_height + 20)) + (button_height // 2)))
            self.option_rects.append(text_rect)
            surface.blit(text_surf, text_rect)

    def handle_input(self, event):
        """
        Handles input events for the menu.

        Args:
            event (pygame.event.Event): The event to handle.

        Returns:
            int or None: The index of the selected option if an option is selected, None otherwise.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, option_rect in enumerate(self.option_rects):
                if option_rect.collidepoint(mouse_pos):
                    self.selected_option = i
                    return self.selected_option
        return None
