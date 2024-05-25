
from settings import *
from ui_ux import Menu

class Game:
    """
    The Game class represents the main game loop and handles game states, events, and updates.

    Attributes:
        display_surface: The main display surface for the game.
        clock: The game clock to manage frame rate.
        running: A boolean indicating whether the game is running.
        menu_options: The list of menu options.
        menu: The Menu object for handling the game menu.
        font: The font used for rendering text.
        state: The current state of the game (e.g., 'menu', 'game', 'guide', 'game_over').
        guide_text: A list of guide instructions for the player.
        
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
        self.font = pygame.font.Font(None, 36)
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
    def draw_guide(self):
        """Draws the game guide on the screen."""
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
                self.draw_guide()
    
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()
