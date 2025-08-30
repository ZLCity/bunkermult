import pygame
import sys
import os

# --- Path Setup ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from game.world.grid import Grid

# --- Initialization ---
pygame.init()

# --- Screen Settings ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Astromorph")

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (170, 170, 170)
GRID_COLOR = (40, 40, 40) # New color for the grid lines

# --- Fonts ---
font = pygame.font.Font(None, 50)

# --- Game State ---
game_state = {'current': 'main_menu'}

# --- Button Class ---
class Button:
    def __init__(self, x, y, width, height, text, action=None, action_args=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.action_args = action_args if action_args is not None else []

    def draw(self, surface):
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action(*self.action_args)

# --- State Change Function ---
def set_state(new_state):
    game_state['current'] = new_state
    print(f"Changing state to: {new_state}")

# --- Game Functions ---
def quit_game():
    print("Quitting game.")
    pygame.quit()
    sys.exit()

# --- Grid Drawing Function ---
CELL_SIZE = 32
def draw_grid(surface, grid):
    for x in range(0, grid.width * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, grid.height * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))


# --- Screens / States ---

# Main Menu Screen
menu_buttons = [
    Button(300, 150, 200, 50, "Start Game", set_state, ['gameplay']),
    Button(300, 250, 200, 50, "Options", set_state, ['options']),
    Button(300, 350, 200, 50, "Quit", quit_game)
]

def main_menu_screen():
    screen.fill(GRAY)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        for button in menu_buttons:
            button.handle_event(event)

    for button in menu_buttons:
        button.draw(screen)

# Gameplay Screen
game_grid = Grid(width=SCREEN_WIDTH // CELL_SIZE, height=SCREEN_HEIGHT // CELL_SIZE)
def gameplay_screen():
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                set_state('main_menu')

    # Drawing
    screen.fill(BLACK)
    draw_grid(screen, game_grid)

# Options Screen (Placeholder)
def options_screen():
    screen.fill(GRAY)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                set_state('main_menu')

# --- Main Application Loop ---
if __name__ == "__main__":
    while True:
        if game_state['current'] == 'main_menu':
            main_menu_screen()
        elif game_state['current'] == 'gameplay':
            gameplay_screen()
        elif game_state['current'] == 'options':
            options_screen()

        pygame.display.flip()
