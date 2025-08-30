import pygame
import sys

# --- Initialization ---
pygame.init()

# --- Screen Settings ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Astromorph - Main Menu")

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (170, 170, 170)

# --- Fonts ---
font = pygame.font.Font(None, 50)

# --- Button Class ---
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action

    def draw(self, surface):
        # Draw button rectangle
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2) # Border

        # Draw button text
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

# --- Game Functions (Placeholders) ---
def start_game():
    print("Action: Start Game")
    # In the future, this will switch to the main game state.

def show_options():
    print("Action: Show Options")
    # In the future, this will open an options menu.

def quit_game():
    print("Quitting game.")
    pygame.quit()
    sys.exit()

# --- Create Buttons ---
button_width = 300
button_height = 70
button_x = (SCREEN_WIDTH - button_width) / 2

buttons = [
    Button(button_x, 150, button_width, button_height, "Start Game", start_game),
    Button(button_x, 250, button_width, button_height, "Options", show_options),
    Button(button_x, 350, button_width, button_height, "Quit", quit_game)
]

# --- Main Game Loop ---
def main_menu():
    while True: # Loop indefinitely until an action exits the game
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            for button in buttons:
                button.handle_event(event)

        # Drawing
        screen.fill(GRAY) # Background
        for button in buttons:
            button.draw(screen)

        # Update the display
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
