import pygame
import sys
import os
import random

# --- Path Setup ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from game.world.grid import Grid
from game.crafting.item import Item
from game.crafting.inventory import Inventory
from game.structures.bio_forge import BioForge

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
PLAYER_COLOR = (0, 150, 255)
BUILDING_COLORS = {"Bio-Forge": (200, 100, 0)}
RESOURCE_COLORS = {"Raw Ore": (139, 69, 19)}
MENU_OVERLAY_COLOR = (0, 0, 0, 150)

# --- Fonts ---
font = pygame.font.Font(None, 50)
hud_font = pygame.font.Font(None, 30)
crafting_font = pygame.font.Font(None, 35)

# --- Game Constants ---
CELL_SIZE = 32

# --- Game Data: Items & Recipes ---
raw_ore_item = Item("Raw Ore")
bio_forge_item = Item("Bio-Forge")
crafting_recipes = {bio_forge_item: {raw_ore_item: 10}}

# --- Game State & UI Toggles ---
game_state = {'current': 'main_menu'}
crafting_menu_open = False
in_build_mode = False
item_to_build = None

# --- Player Class ---
class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.inventory = Inventory()
    def move(self, dx, dy, grid):
        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < grid.width and 0 <= new_y < grid.height:
            self.x, self.y = new_x, new_y
    def mine(self, node):
        self.inventory.add(node.item, 1)
        node.amount -= 1
    def craft(self, item_to_craft):
        recipe = crafting_recipes.get(item_to_craft)
        if recipe and self.inventory.has_items(recipe):
            for item, qty in recipe.items(): self.inventory.remove(item, qty)
            self.inventory.add(item_to_craft, 1)
            print(f"Successfully crafted {item_to_craft.name}!")
        else:
            print(f"Not enough resources to craft {item_to_craft.name}.")
    def draw(self, surface):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, PLAYER_COLOR, rect)

# --- World Object Classes ---
class ResourceNode:
    def __init__(self, x, y, resource_item, amount):
        self.x, self.y, self.item, self.amount = x, y, resource_item, amount
        self.color = RESOURCE_COLORS.get(self.item.name, (255, 0, 255))
    def draw(self, surface):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, self.color, rect)

class PlacedBuilding:
    def __init__(self, x, y, item_type):
        self.x, self.y, self.item = x, y, item_type
        self.color = BUILDING_COLORS.get(self.item.name, (0, 200, 0))
    def draw(self, surface):
        rect = pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, self.color, rect)

# --- Button Class ---
class Button:
    def __init__(self, x, y, w, h, text, action=None, args=None):
        self.rect, self.text, self.action, self.args = pygame.Rect(x, y, w, h), text, action, args or []
    def draw(self, surface):
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surf = font.render(self.text, True, BLACK)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos) and self.action:
            self.action(*self.args)
            return True
        return False

# --- State Change & Game Functions ---
def set_state(new_state):
    global crafting_menu_open, in_build_mode, item_to_build
    if new_state == 'gameplay':
        crafting_menu_open = in_build_mode = False; item_to_build = None
    game_state['current'] = new_state

def quit_game(): pygame.quit(); sys.exit()
def toggle_crafting_menu():
    global crafting_menu_open;
    if not in_build_mode: crafting_menu_open = not crafting_menu_open
def toggle_build_mode():
    global in_build_mode, item_to_build, crafting_menu_open
    if in_build_mode:
        in_build_mode = False; item_to_build = None
    else:
        if player.inventory.items.get(bio_forge_item, 0) > 0:
            in_build_mode = True; item_to_build = bio_forge_item; crafting_menu_open = False
            print("Entering build mode for Bio-Forge. Click to place.")
        else:
            print("No Bio-Forge in inventory.")

# --- Drawing Functions ---
def draw_grid(surface, grid):
    for x in range(0, grid.width*CELL_SIZE, CELL_SIZE): pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, grid.height*CELL_SIZE, CELL_SIZE): pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

def draw_hud(surface, inventory):
    y = 10; surface.blit(hud_font.render("Inventory:", True, WHITE), (10, y)); y += 25
    if not inventory.items: surface.blit(hud_font.render("- Empty -", True, GRAY), (15, y))
    else:
        for item, quant in inventory.items.items(): surface.blit(hud_font.render(f"- {item.name}: {quant}", True, WHITE), (15, y)); y += 20

def draw_crafting_menu(events):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill(MENU_OVERLAY_COLOR); screen.blit(overlay, (0, 0))
    menu_rect = pygame.Rect(150, 100, 500, 400); pygame.draw.rect(screen, GRAY, menu_rect); pygame.draw.rect(screen, WHITE, menu_rect, 2)
    screen.blit(font.render("Crafting", True, WHITE), (menu_rect.x + 20, menu_rect.y + 20))
    y_offset = menu_rect.y + 80
    for item, ingredients in crafting_recipes.items():
        screen.blit(crafting_font.render(f"Craft {item.name}", True, WHITE), (menu_rect.x + 30, y_offset))
        ing_y = y_offset + 35
        for ing_item, ing_qty in ingredients.items():
            screen.blit(hud_font.render(f"- {ing_qty} {ing_item.name}", True, LIGHT_GRAY), (menu_rect.x + 40, ing_y)); ing_y += 25
        btn = Button(menu_rect.x + 350, y_offset, 120, 40, "Craft", player.craft, [item]); btn.draw(screen)
        for e in events:
            if btn.handle_event(e): toggle_crafting_menu()
        y_offset += 100

def draw_ghost_building(surface, item):
    mx, my = pygame.mouse.get_pos(); gx, gy = mx // CELL_SIZE, my // CELL_SIZE
    px, py = gx * CELL_SIZE, gy * CELL_SIZE
    ghost_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    color = list(BUILDING_COLORS.get(item.name, (0, 255, 0))) + [128]
    pygame.draw.rect(ghost_surf, color, (0, 0, CELL_SIZE, CELL_SIZE))
    surface.blit(ghost_surf, (px, py))

# --- Game World Objects ---
player = Player(x=10, y=10)
game_grid = Grid(width=SCREEN_WIDTH // CELL_SIZE, height=SCREEN_HEIGHT // CELL_SIZE)
resource_nodes, buildings = [], []

def generate_resources():
    resource_nodes.clear()
    for _ in range(10):
        x, y = random.randint(0, game_grid.width - 1), random.randint(0, game_grid.height - 1)
        if (x, y) != (player.x, player.y) and not any(n.x == x and n.y == y for n in resource_nodes):
            resource_nodes.append(ResourceNode(x, y, raw_ore_item, random.randint(5, 15)))

# --- Screens / States ---
def main_menu_screen():
    buttons = [Button(300,150,200,50,"Start Game",set_state,['gameplay']), Button(300,250,200,50,"Options",set_state,['options']), Button(300,350,200,50,"Quit",quit_game)]
    screen.fill(GRAY); events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT: quit_game()
        for btn in buttons: btn.handle_event(e)
    for btn in buttons: btn.draw(screen)

def gameplay_screen():
    global in_build_mode, crafting_menu_open
    events = pygame.event.get()
    if not crafting_menu_open and not in_build_mode:
        for e in events:
            if e.type == pygame.QUIT: quit_game()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: set_state('main_menu')
                elif e.key == pygame.K_c: toggle_crafting_menu()
                elif e.key == pygame.K_b: toggle_build_mode()
                elif e.key in (pygame.K_UP, pygame.K_w): player.move(0, -1, game_grid)
                elif e.key in (pygame.K_DOWN, pygame.K_s): player.move(0, 1, game_grid)
                elif e.key in (pygame.K_LEFT, pygame.K_a): player.move(-1, 0, game_grid)
                elif e.key in (pygame.K_RIGHT, pygame.K_d): player.move(1, 0, game_grid)
                elif e.key == pygame.K_SPACE:
                    node = next((n for n in resource_nodes if n.x == player.x and n.y == player.y), None)
                    if node:
                        player.mine(node);
                        if node.amount <= 0: resource_nodes.remove(node)
    elif crafting_menu_open:
        for e in events:
            if e.type == pygame.QUIT: quit_game()
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_c): toggle_crafting_menu()
    elif in_build_mode:
        for e in events:
            if e.type == pygame.QUIT: quit_game()
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_b): toggle_build_mode()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                gx, gy = e.pos[0] // CELL_SIZE, e.pos[1] // CELL_SIZE
                occupied = any(n.x==gx and n.y==gy for n in resource_nodes) or any(b.x==gx and b.y==gy for b in buildings) or (player.x==gx and player.y==gy)
                if not occupied:
                    buildings.append(PlacedBuilding(gx, gy, item_to_build)); player.inventory.remove(item_to_build, 1); toggle_build_mode()
                else: print("Cannot build on an occupied tile.")

    screen.fill(BLACK); draw_grid(screen, game_grid)
    for res in resource_nodes: res.draw(screen)
    for bld in buildings: bld.draw(screen)
    player.draw(screen); draw_hud(screen, player.inventory)
    if crafting_menu_open: draw_crafting_menu(events)
    if in_build_mode: draw_ghost_building(screen, item_to_build)

def options_screen():
    screen.fill(GRAY); events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT: quit_game()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: set_state('main_menu')

# --- Main Application Loop ---
if __name__ == "__main__":
    generate_resources()
    while True:
        if game_state['current'] == 'main_menu': main_menu_screen()
        elif game_state['current'] == 'gameplay': gameplay_screen()
        elif game_state['current'] == 'options': options_screen()
        pygame.display.flip()
