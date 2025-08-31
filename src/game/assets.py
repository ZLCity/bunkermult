import zipfile
import io

# --- Asset Storage ---
# These are placeholders. They will be replaced by Pygame surfaces
# when load_assets_from_url() is called.
PLAYER_SPRITE = None
RESOURCE_SPRITES = {}
TERRAIN_TILES = {}
STRUCTURE_SPRITES = {}
DEFAULT_SPRITE = "placeholder" # Using a string placeholder

# --- Asset Loading Function ---
def load_assets_from_url():
    """
    Downloads asset zip and loads images into Pygame surfaces.
    Pygame and requests are imported here to prevent tests from depending on them.
    """
    import pygame
    import requests
    global PLAYER_SPRITE, RESOURCE_SPRITES, TERRAIN_TILES, STRUCTURE_SPRITES, DEFAULT_SPRITE

    # Define a default placeholder surface in case loading fails
    DEFAULT_SPRITE = pygame.Surface((32, 32))
    DEFAULT_SPRITE.fill((255, 0, 255)) # Magenta for easy error spotting

    asset_zip_url = "https://kenney.nl/media/pages/assets/sci-fi-rts/fe54b36f65-1677693650/kenney_sci-fi-rts.zip"

    asset_paths = {
        "player": "PNG/Default size/Unit/scifiUnit_03.png",
        "ore": "PNG/Default size/Environment/scifiEnvironment_08.png",
        "flora": "PNG/Default size/Environment/scifiEnvironment_13.png",
        "biomass": "PNG/Default size/Environment/scifiEnvironment_02.png",
        "ground": "PNG/Default size/Tile/scifiTile_15.png",
        "bio-forge": "PNG/Default size/Structure/scifiStructure_04.png"
    }

    try:
        print("Downloading assets from URL...")
        response = requests.get(asset_zip_url)
        response.raise_for_status()
        print("Download complete.")

        zip_file = zipfile.ZipFile(io.BytesIO(response.content))

        print("Loading sprites from in-memory zip file...")

        player_data = zip_file.read(asset_paths["player"])
        PLAYER_SPRITE = pygame.image.load(io.BytesIO(player_data), "player.png").convert_alpha()

        ore_data = zip_file.read(asset_paths["ore"])
        RESOURCE_SPRITES["Raw Ore"] = pygame.image.load(io.BytesIO(ore_data), "ore.png").convert_alpha()

        flora_data = zip_file.read(asset_paths["flora"])
        RESOURCE_SPRITES["Fibrous Flora"] = pygame.image.load(io.BytesIO(flora_data), "flora.png").convert_alpha()

        biomass_data = zip_file.read(asset_paths["biomass"])
        RESOURCE_SPRITES["Biomass"] = pygame.image.load(io.BytesIO(biomass_data), "biomass.png").convert_alpha()

        ground_data = zip_file.read(asset_paths["ground"])
        TERRAIN_TILES["ground"] = pygame.image.load(io.BytesIO(ground_data), "ground.png").convert_alpha()

        forge_data = zip_file.read(asset_paths["bio-forge"])
        STRUCTURE_SPRITES["Bio-forge"] = pygame.image.load(io.BytesIO(forge_data), "bio-forge.png").convert_alpha()

        print("All required assets loaded successfully.")

    except Exception as e:
        print(f"FATAL: Asset loading failed: {e}")
        # Populate with placeholders on failure
        PLAYER_SPRITE = DEFAULT_SPRITE
        TERRAIN_TILES["ground"] = DEFAULT_SPRITE
        STRUCTURE_SPRITES["Bio-forge"] = DEFAULT_SPRITE


def get_resource_sprite(resource_name):
    """Returns the sprite for a given resource name, or a default if not found."""
    # This might be called by tests, so it can't depend on pygame being initialized
    if isinstance(DEFAULT_SPRITE, str): # Check if assets are not loaded yet
        return None # Return None or a placeholder that doesn't require pygame
    return RESOURCE_SPRITES.get(resource_name, DEFAULT_SPRITE)
