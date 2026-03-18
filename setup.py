import pygame
import pygame_gui
import os, json
import sys

# Constants for the table size in mm and image path
TABLE_WIDTH_MM = 3000
TABLE_HEIGHT_MM = 2000
IMAGE_PATH = 'botikplaymat.jpg'  # Update this to your image path

# Screen setup
#il faut respecter la prortion 3/2 pour l'image du terrain
Screen_WIDTH, Screen_HEIGHT = 1200, 600
FIELD_WIDTH, FIELD_HEIGHT = 900,600 

# j'ai du créer cette fonction bizarre avec gpt car il y avait un problème avec l'importation d'une police par defaut
def make_theme_with_pygame_font(theme_filename="theme.json", size=16):
    pygame.font.init()
    # police par défaut de Pygame (freesansbold.ttf) + chemin absolu
    font_name = pygame.font.get_default_font()
    font_path = os.path.join(os.path.dirname(pygame.__file__), font_name)

    theme = {
        "defaults": {
            "font": {
                "name": font_path,   # <- chemin absolu garanti
                "size": size
            }
        }
    }
    theme_path = os.path.join(os.path.dirname(__file__), theme_filename)
    with open(theme_path, "w", encoding="utf-8") as f:
        json.dump(theme, f)
    return theme_path

def resource_path(relative_path):
    """Récupère le chemin absolu d'une ressource, que ce soit en .exe ou en dev."""
    try:
        base_path = sys._MEIPASS  # Dossier temporaire PyInstaller
    except Exception:
        base_path = os.path.abspath(".")  # Mode normal (dev)

    return os.path.join(base_path, relative_path)

def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((Screen_WIDTH, Screen_HEIGHT))
    return screen

def load_image():
    image = pygame.image.load(resource_path(IMAGE_PATH))
    img_width, img_height = image.get_size()
    return image, img_width, img_height

def init():
    theme_path_default = make_theme_with_pygame_font()
    manager = pygame_gui.UIManager((Screen_WIDTH, Screen_HEIGHT), theme_path = theme_path_default)
    screen = init_pygame()
    vinyle, img_width, img_height = load_image()
    scaled_vinyle = pygame.transform.scale(vinyle, (FIELD_WIDTH, FIELD_HEIGHT))
    return screen, scaled_vinyle, manager