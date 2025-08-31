import pygame
import sys
import os
import random

# --- Path Setup ---
# Ensures that the 'src' directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# --- Refactored Imports ---
from game import settings
from game import assets
from game.world.grid import Grid
from game.crafting.item import Item
from game.crafting.recipe import Recipe
from game.entities.player import Player
from game.world.resource_node import ResourceNode
from game.structures.bio_forge import BioForge
from game.ui.button import Button

# --- Initialization ---
pygame.init()

# --- Screen From Settings ---
screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
pygame.display.set_caption(settings.TITLE)

# --- Colors (those that remain) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

# --- Game State ---
game_state = {'current': 'main_menu'}
build_mode_on = False

# --- Recipes & Costs ---
# This should eventually move to a data file, but is fine here for now.
raw_ore_item = Item("Raw Ore")
metal_plate_item = Item("Metal Plate")
fibrous_flora_item = Item("Fibrous Flora")
biomass_item = Item("Biomass")

BIOFORGE_COST = {raw_ore_item: 10}
DEFAULT_BIOFORGE_RECIPE = Recipe(inputs={raw_ore_item: 2}, outputs={metal_plate_item: 1})

# --- State Management ---
def set_state(new_state):
    game_state['current'] = new_state
    print(f"Changing state to: {new_state}")

def quit_game():
    print("Quitting game.")
    pygame.quit()
    sys.exit()

# --- Drawing Functions ---
def draw_background(surface, grid):
    ground_tile = assets.TERRAIN_TILES.get("ground")
    if ground_tile:
        for x in range(grid.width):
            for y in range(grid.height):
                surface.blit(ground_tile, (x * settings.CELL_SIZE, y * settings.CELL_SIZE))

def draw_hud(surface, inventory):
    hud_font = pygame.font.Font(None, 30) # Create font on-the-fly
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

# --- Game World Setup ---
player = Player(x=10, y=10)
game_grid = Grid(width=settings.SCREEN_WIDTH // settings.CELL_SIZE, height=settings.SCREEN_HEIGHT // settings.CELL_SIZE)
resource_nodes = []
placed_structures = []

def generate_resources():
    resource_nodes.clear()

    # Define the types of resources that can spawn
    resource_types = [
        (raw_ore_item, 15),
        (fibrous_flora_item, 10),
        (biomass_item, 10)
    ]

    total_patches = 25 # Total number of resource patches to generate

    for _ in range(total_patches):
        # Choose a random resource type to spawn
        item_type, max_amount = random.choice(resource_types)

        x = random.randint(0, game_grid.width - 1)
        y = random.randint(0, game_grid.height - 1)

        # Ensure we don't spawn on the player or another node
        is_occupied = (x, y) == (player.x, player.y) or any(node.x == x and node.y == y for node in resource_nodes)
        if not is_occupied:
            amount = random.randint(max_amount // 2, max_amount)
            node = ResourceNode(x, y, item_type, amount)
            resource_nodes.append(node)

# --- Screens / States Logic ---
def main_menu_screen(buttons):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()
        for button in buttons:
            button.handle_event(event)

    screen.fill(GRAY)
    for button in buttons:
        button.draw(screen)

def gameplay_screen():
    global build_mode_on # Use the global build_mode_on flag

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()

        if event.type == pygame.MOUSEBUTTONDOWN and build_mode_on:
            if event.button == 1: # Left click
                grid_x = event.pos[0] // settings.CELL_SIZE
                grid_y = event.pos[1] // settings.CELL_SIZE

                # TODO: Check if the tile is already occupied before building

                print(f"Attempting to build at ({grid_x}, {grid_y})")

                # Check if player has enough resources
                if player.inventory.has_items(BIOFORGE_COST):
                    player.inventory.remove_items(BIOFORGE_COST)

                    # Create and place the BioForge
                    new_forge = BioForge(recipe=DEFAULT_BIOFORGE_RECIPE, processing_time=100, output_direction=(0,1), power_consumption=10)
                    new_forge.x = grid_x
                    new_forge.y = grid_y
                    placed_structures.append(new_forge)
                    print(f"Bio-forge built at ({grid_x}, {grid_y})!")
                else:
                    print("Not enough resources to build a Bio-forge!")

                build_mode_on = False # Exit build mode after attempting to build

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                build_mode_on = not build_mode_on
                print(f"Build mode toggled: {'ON' if build_mode_on else 'OFF'}")

            if not build_mode_on:
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

    # --- Update World ---
    for structure in placed_structures:
        structure.update(grid=game_grid, has_power=True) # Assuming power for now

    # --- Drawing ---
    draw_background(screen, game_grid)
    for node in resource_nodes:
        node.draw(screen)
    for structure in placed_structures:
        structure.draw(screen)
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
def main():
    assets.load_assets_from_url()
    generate_resources()

    menu_buttons = [
        Button(300, 150, 200, 50, "Start Game", set_state, ['gameplay']),
        Button(300, 250, 200, 50, "Options", set_state, ['options']),
        Button(300, 350, 200, 50, "Quit", quit_game)
    ]

    clock = pygame.time.Clock()

    while True:
        if game_state['current'] == 'main_menu':
            main_menu_screen(menu_buttons)
        elif game_state['current'] == 'gameplay':
            gameplay_screen()
        elif game_state['current'] == 'options':
            options_screen()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
