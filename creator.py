import pygame
import json 
import os
import sys
from config_manager import initialize_quadrants

JSON_FILE = "quadrants.json"


def show_creator(screen):
    # Récupérer la configuration
    config, _ = initialize_quadrants()
    
    # Initialisation de Pygame
    pygame.init()

    # Définition des constantes
    WIDTH, HEIGHT = 675, 500
    GRID_SIZE = 4
    CELL_SIZE = 100
    PALETTE_X = WIDTH - (CELL_SIZE * 1.5)
    MENU_Y = HEIGHT - 50  # Position du menu

    # Dictionnaire des couleurs avec leurs propriétés
    COLOR_DATA = {
        (250, 250, 0): {"image": "img/yellow.png", "value": 1},  # Jaune → 1
        (0, 0, 250): {"image": "img/blue.png", "value": 3},     # Bleu → 3
        (0, 250, 0): {"image": "img/green.png", "value": 2},    # Vert → 2
        (250, 0, 0): {"image": "img/red.png", "value": 4},       # Rouge → 4
    }

    # Chemin du dossier contenant les images
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    SAVE_DIR = os.path.join(SCRIPT_DIR, config["quadrants_folder"])
    
    # Créer le dossier de sauvegarde s'il n'existe pas
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Chargement des images (si elles existent)
    images = {}
    for color, data in COLOR_DATA.items():
        img_path = os.path.join(SCRIPT_DIR, data["image"])
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)
            images[color] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        else:
            print(f"Image {data['image']} introuvable, la couleur {color} sera utilisée.")

    # Création de la fenêtre
    pygame.display.set_caption("Constructeur de Quadrant")

    class Quadrant:
        def __init__(self):
            self.grid = [[(255, 255, 255) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
            self.history = []
            self.future = []

        def draw(self, screen):
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    color = self.grid[row][col]
                    if color in images:
                        screen.blit(images[color], (col * CELL_SIZE, row * CELL_SIZE))
                    else:
                        pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(screen, (0, 0, 0), (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

        def update_color(self, x, y, color):
            col = x // CELL_SIZE
            row = y // CELL_SIZE
            if 0 <= col < GRID_SIZE and 0 <= row < GRID_SIZE:
                self.history.append([row.copy() for row in self.grid])
                self.grid[row][col] = color
                self.future.clear()

        def undo(self):
            if self.history:
                self.future.append([row.copy() for row in self.grid])
                self.grid = self.history.pop()

        def redo(self):
            if self.future:
                self.history.append([row.copy() for row in self.grid])
                self.grid = self.future.pop()

        def reset(self):
            self.history.append([row.copy() for row in self.grid])
            self.grid = [[(250, 250, 250) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        def good_message(self, screen, message):
            font = pygame.font.Font(None, 28) 
            text_surface = font.render(message, True, (0, 250, 0))
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, HEIGHT - 70))
            screen.blit(text_surface, text_rect)
            pygame.display.update()
            pygame.time.delay(2000)  # Délai pour afficher le message

        def show_error_message(self, screen, message):
            font = pygame.font.Font(None, 28)  # Taille du texte
            text_surface = font.render(message, True, (250, 0, 0))  # Texte en rouge
            text_rect = text_surface.get_rect(center=(screen.get_width() // 2, HEIGHT - 70))
            screen.blit(text_surface, text_rect)
            pygame.display.update()
            pygame.time.delay(2000)  # Affichage du message pendant 2 secondes

        def save(self):
            # Vérification des cases blanches
            has_white_cells = False
            for row in self.grid:
                for cell in row:
                    # Vérifier si la cellule est blanche (255, 255, 255) 
                    # ou si elle n'est pas dans notre ensemble de couleurs valides
                    if cell == (255, 255, 255) or cell == (250, 250, 250):
                        has_white_cells = True
                        break
                if has_white_cells:
                    break
                    
            if has_white_cells:
                self.show_error_message(screen, "Impossible de sauvegarder : cases blanches !")
                return

            # Charger les données JSON existantes ou créer un nouveau dictionnaire
            data = {}
            json_path = os.path.join(SCRIPT_DIR, JSON_FILE)
            
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r") as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    # Si le fichier existe mais n'est pas un JSON valide, on le réinitialise
                    data = {}
            
            # Déterminer le prochain ID de quadrant
            next_id = 1
            while f"quadrant_{next_id}" in data:
                next_id += 1
                
            quadrant_id = f"quadrant_{next_id}"
            
            # Sauvegarde de l'image
            img_filename = f"quadrant_{next_id}.png"
            img_path = os.path.join(SAVE_DIR, img_filename)
            
            # Création de la surface
            quadrant_surface = pygame.Surface((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
            quadrant_surface.fill((255, 255, 255))

            # Dessin de la grille
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    color = self.grid[row][col]
                    if color in images:
                        quadrant_surface.blit(images[color], (col * CELL_SIZE, row * CELL_SIZE))
                    else:
                        pygame.draw.rect(quadrant_surface, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(quadrant_surface, (0, 0, 0), (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

            pygame.image.save(quadrant_surface, img_path)
            
            # Conversion des couleurs en valeurs numériques pour chaque cellule
            grid_data = []
            for row in self.grid:
                row_data = []
                for cell in row:
                    if cell in COLOR_DATA:
                        row_data.append(COLOR_DATA[cell]["value"])
                    else:
                        row_data.append(0)  # Valeur par défaut si couleur inconnue
                grid_data.append(row_data)
            
            # Création de l'entrée dans le dictionnaire pour ce quadrant
            data[quadrant_id] = {
                "image_path": os.path.abspath(img_path),  # Chemin absolu
                "grid": grid_data
            }

            # Sauvegarde du fichier JSON
            with open(json_path, "w") as f:
                json.dump(data, f, indent=4)

            self.good_message(screen, f"Quadrant {next_id} sauvegardé avec succès!")
            
           
            
    class Palette:
        def __init__(self):
            self.colors = list(COLOR_DATA.keys())
            self.rects = [(pygame.Rect(PALETTE_X, i * (CELL_SIZE + 5), CELL_SIZE, CELL_SIZE), color) for i, color in enumerate(self.colors)]
            self.selected_color = None

        def draw(self, screen):
            for rect, color in self.rects:
                if color in images:
                    screen.blit(images[color], rect.topleft)
                else:
                    pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 2)

            # Affichage de la couleur sélectionnée (taille réduite à 40x40)
            if self.selected_color:
                preview_rect = pygame.Rect(PALETTE_X - 50, 10, 40, 40)
                if self.selected_color in images:
                    preview_image = pygame.transform.scale(images[self.selected_color], (40, 40))
                    screen.blit(preview_image, preview_rect.topleft)
                else:
                    pygame.draw.rect(screen, self.selected_color, preview_rect)

        def get_color_at(self, x, y):
            for rect, color in self.rects:
                if rect.collidepoint(x, y):
                    self.selected_color = color
                    return color
            return None

    class Menu:
        def __init__(self):
            self.buttons = {
                "Retour": pygame.Rect(20, MENU_Y, 100, 40),
                "Retour arrière": pygame.Rect(130, MENU_Y, 150, 40),
                "Avancer": pygame.Rect(290, MENU_Y, 100, 40),
                "Reset": pygame.Rect(400, MENU_Y, 100, 40),
                "Sauvegarder": pygame.Rect(510, MENU_Y, 150, 40)
            }

        def draw(self, screen):
            for text, rect in self.buttons.items():
                pygame.draw.rect(screen, (200, 200, 200), rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 2)
                font = pygame.font.Font(None, 24)
                screen.blit(font.render(text, True, (0, 0, 0)), (rect.x + 10, rect.y + 10))

        def get_action(self, x, y):
            for text, rect in self.buttons.items():
                if rect.collidepoint(x, y):
                    return text
            return None

    # Initialisation des objets
    quadrant = Quadrant()
    palette = Palette()
    menu = Menu()

    # Boucle principale
    running = True
    while running:
        screen.fill((255, 255, 255))
        quadrant.draw(screen)
        palette.draw(screen)
        menu.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if y < HEIGHT - 50:
                    color = palette.get_color_at(x, y)
                    if not color and palette.selected_color:
                        quadrant.update_color(x, y, palette.selected_color)
                else:
                    action = menu.get_action(x, y)
                    if action == "Retour":
                        return
                    elif action == "Retour arrière":
                        quadrant.undo()
                    elif action == "Avancer":
                        quadrant.redo()
                    elif action == "Reset":
                        quadrant.reset()
                    elif action == "Sauvegarder":
                        quadrant.save()

        pygame.display.flip()


def run_creator(screen):
    show_creator(screen)