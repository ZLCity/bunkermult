import pygame
import sys
import os
import random

# --- Path Setup ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from game.world.grid import Grid
from game.crafting.item import Item
from game.crafting.inventory import Inventory

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
GRID_COLOR = (40, 40, 40)
PLAYER_COLOR = (0, 150, 255) # Blue for the player
RESOURCE_COLORS = {
    "Raw Ore": (139, 69, 19) # Brown
}


# --- Fonts ---
font = pygame.font.Font(None, 50)
hud_font = pygame.font.Font(None, 30)


# --- Game Constants ---
CELL_SIZE = 32

# --- Game State ---
game_state = {'current': 'main_menu'}

# --- Player Class ---
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.inventory = Inventory()

    def move(self, dx, dy, grid):
        new_x = self.x + dx
        new_y = self.y + dy
        # Boundary check
        if 0 <= new_x < grid.width and 0 <= new_y < grid.height:
            self.x = new_x
            self.y = new_y

    def mine(self, node):
        print(f"Mining {node.item.name}...")
        self.inventory.add(node.item, 1)
        node.amount -= 1
        print(f"Inventory: {self.inventory.items}")

    def draw(self, surface):
        pixel_x = self.x * CELL_SIZE
        pixel_y = self.y * CELL_SIZE
        player_rect = pygame.Rect(pixel_x, pixel_y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, PLAYER_COLOR, player_rect)

# --- Resource Node Class ---
class ResourceNode:
    def __init__(self, x, y, resource_item, amount):
        self.x = x
        self.y = y
        self.item = resource_item
        self.amount = amount
        self.color = RESOURCE_COLORS.get(self.item.name, (255, 0, 255)) # Default to magenta

    def draw(self, surface):
        pixel_x = self.x * CELL_SIZE
        pixel_y = self.y * CELL_SIZE
        resource_rect = pygame.Rect(pixel_x, pixel_y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, self.color, resource_rect)

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

# --- Drawing Functions ---
def draw_grid(surface, grid):
    for x in range(0, grid.width * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, grid.height * CELL_SIZE, CELL_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

def draw_hud(surface, inventory):
    y_offset = 10
    inventory_title_surf = hud_font.render("Inventory:", True, WHITE)
    surface.blit(inventory_title_surf, (10, y_offset))
    y_offset += 25

    if not inventory.items:
        empty_text_surf = hud_font.render("- Empty -", True, GRAY)
        surface.blit(empty_text_surf, (15, y_offset))
    else:
        for item, quantity in inventory.items.items():
            item_text = f"- {item.name}: {quantity}"
            text_surf = hud_font.render(item_text, True, WHITE)
            surface.blit(text_surf, (15, y_offset))
            y_offset += 20

# --- Game World Objects ---
player = Player(x=10, y=10)
game_grid = Grid(width=SCREEN_WIDTH // CELL_SIZE, height=SCREEN_HEIGHT // CELL_SIZE)
resource_nodes = []

def generate_resources():
    resource_nodes.clear() # Clear previous resources
    raw_ore_item = Item("Raw Ore")
    for _ in range(10): # Generate 10 ore patches
        x = random.randint(0, game_grid.width - 1)
        y = random.randint(0, game_grid.height - 1)
        is_occupied = (x, y) == (player.x, player.y) or any(node.x == x and node.y == y for node in resource_nodes)
        if not is_occupied:
            node = ResourceNode(x, y, raw_ore_item, random.randint(5, 15))
            resource_nodes.append(node)

# --- Screens / States ---

def main_menu_screen():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        for button in menu_buttons:
            button.handle_event(event)

    screen.fill(GRAY)
    for button in menu_buttons:
        button.draw(screen)

def gameplay_screen():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                set_state('main_menu')
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                player.move(dx=0, dy=-1, grid=game_grid)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                player.move(dx=0, dy=1, grid=game_grid)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                player.move(dx=-1, dy=0, grid=game_grid)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player.move(dx=1, dy=0, grid=game_grid)
            elif event.key == pygame.K_SPACE:
                target_node = next((node for node in resource_nodes if node.x == player.x and node.y == player.y), None)
                if target_node:
                    player.mine(target_node)
                    if target_node.amount <= 0:
                        resource_nodes.remove(target_node)
                        print("Resource depleted.")

    screen.fill(BLACK)
    draw_grid(screen, game_grid)
    for node in resource_nodes:
        node.draw(screen)
    player.draw(screen)
    draw_hud(screen, player.inventory)

def options_screen():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                set_state('main_menu')
    screen.fill(GRAY)

# --- Main Application Loop ---
if __name__ == "__main__":
    generate_resources()
    menu_buttons = [
        Button(300, 150, 200, 50, "Start Game", set_state, ['gameplay']),
        Button(300, 250, 200, 50, "Options", set_state, ['options']),
        Button(300, 350, 200, 50, "Quit", quit_game)
    ]

    while True:
        if game_state['current'] == 'main_menu':
            main_menu_screen()
        elif game_state['current'] == 'gameplay':
            gameplay_screen()
        elif game_state['current'] == 'options':
            options_screen()

        pygame.display.flip()
