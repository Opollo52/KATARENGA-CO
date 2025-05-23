import pygame
import json 
import os
import sys
from config_manager import initialize_quadrants

JSON_FILE = "quadrants.json"


def show_creator(screen):
    # Récupérer la config
    config, _ = initialize_quadrants()
    
    pygame.init()

    # Utiliser les dimensions actuelles de l'écran pour le centrage
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    GRID_SIZE = 4
    CELL_SIZE = 100
    GRID_WIDTH = GRID_SIZE * CELL_SIZE
    GRID_HEIGHT = GRID_SIZE * CELL_SIZE
    
    # Centrer la grille
    GRID_X = (WIDTH - GRID_WIDTH) // 2
    GRID_Y = (HEIGHT - GRID_HEIGHT - 80) // 2  # 80 pour l'espace des boutons
    
    # Position de la palette (à droite de la grille)
    PALETTE_WIDTH = CELL_SIZE
    PALETTE_X = GRID_X + GRID_WIDTH + 30
    PALETTE_Y = GRID_Y
    
    # Position de l'indicateur de couleur (à gauche du plateau)
    INDICATOR_X = GRID_X - 200
    INDICATOR_Y = GRID_Y + 70   # Ajusté pour l'affichage horizontal
    
    # Position des boutons du menu (en bas)
    MENU_Y = GRID_Y + GRID_HEIGHT + 20
    
    # Dictionnaire couleurs et img
    COLOR_DATA = {
        (250, 250, 0): {"image": "img/yellow.png", "value": 1},
        (0, 0, 250): {"image": "img/blue.png", "value": 3}, 
        (0, 250, 0): {"image": "img/green.png", "value": 2},
        (250, 0, 0): {"image": "img/red.png", "value": 4}, 
    }

    # Chemin du dossier contenant les images
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    SAVE_DIR = os.path.join(SCRIPT_DIR, config["quadrants_folder"])
    
    # Créer le dossier de sauvegarde s'il n'existe pas
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Chargement de l'image de fond
    background_image = None
    background_path = os.path.join(SCRIPT_DIR, "img/fond.png")
    if os.path.exists(background_path):
        background_image = pygame.image.load(background_path)
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    else:
        print("Image de fond fond.png introuvable, fond blanc utilisé.")

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
                    rect = pygame.Rect(GRID_X + col * CELL_SIZE, GRID_Y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    
                    if color in images:
                        screen.blit(images[color], rect.topleft)
                    else:
                        pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        def update_color(self, x, y, color):
            # Vérifier si le clic est dans la grille
            if x < GRID_X or x >= GRID_X + GRID_WIDTH or y < GRID_Y or y >= GRID_Y + GRID_HEIGHT:
                return
                
            col = (x - GRID_X) // CELL_SIZE
            row = (y - GRID_Y) // CELL_SIZE
            
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
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 70))
            screen.blit(text_surface, text_rect)
            pygame.display.update()
            pygame.time.delay(2000)  # Délai pour afficher le message

        def show_error_message(self, screen, message):
            font = pygame.font.Font(None, 28)  # Taille du texte
            text_surface = font.render(message, True, (250, 0, 0))  # Texte en rouge
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 70))
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
                    rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    
                    if color in images:
                        quadrant_surface.blit(images[color], rect)
                    else:
                        pygame.draw.rect(quadrant_surface, color, rect)
                    pygame.draw.rect(quadrant_surface, (0, 0, 0), rect, 2)

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
            self.rects = []
            
            # Créer les rectangles de la palette, centrés et empilés verticalement
            for i, color in enumerate(self.colors):
                rect = pygame.Rect(
                    PALETTE_X, 
                    PALETTE_Y + i * (CELL_SIZE + 5), 
                    CELL_SIZE, 
                    CELL_SIZE
                )
                self.rects.append((rect, color))
                
            self.selected_color = None

        def draw(self, screen):
            # Titre de la palette
            font = pygame.font.Font(None, 24)
            title = font.render("Palette", True, (0, 0, 0))
            title_rect = title.get_rect(center=(PALETTE_X + CELL_SIZE//2, PALETTE_Y - 20))
            screen.blit(title, title_rect)
            
            for rect, color in self.rects:
                if color in images:
                    screen.blit(images[color], rect.topleft)
                else:
                    pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 2)

            # Affichage de la couleur sélectionnée avec l'indicateur centré en dessous
            if self.selected_color:
                font = pygame.font.Font(None, 24)
                
                # Texte complet "Couleur sélectionnée"
                text_complet = font.render("Couleur sélectionnée:", True, (0, 0, 0))
                text_rect = text_complet.get_rect(topleft=(INDICATOR_X, INDICATOR_Y))
                screen.blit(text_complet, text_rect)
                
                # Taille de l'indicateur de couleur
                indicator_size = 50
                
                # Position de l'indicateur centré en dessous du texte
                indicator_x = INDICATOR_X + text_rect.width//2 - indicator_size//2
                indicator_y = INDICATOR_Y + text_rect.height + 10
                indicator_rect = pygame.Rect(indicator_x, indicator_y, indicator_size, indicator_size)
                
                # Afficher l'image ou la couleur
                if self.selected_color in images:
                    preview_image = pygame.transform.scale(images[self.selected_color], (indicator_size, indicator_size))
                    screen.blit(preview_image, indicator_rect.topleft)
                else:
                    pygame.draw.rect(screen, self.selected_color, indicator_rect)
                
                # Bordure pour l'indicateur
                pygame.draw.rect(screen, (0, 0, 0), indicator_rect, 2)

        def get_color_at(self, x, y):
            for rect, color in self.rects:
                if rect.collidepoint(x, y):
                    self.selected_color = color
                    return color
            return None

    class Menu:
        def __init__(self):
            # Calculer la largeur totale des boutons avec espacement
            button_texts = ["Retour", "Retour arrière", "Avancer", "Reset", "Sauvegarder"]
            button_font = pygame.font.Font(None, 24)
            button_widths = [button_font.render(text, True, (0, 0, 0)).get_width() + 20 for text in button_texts]
            button_heights = [40] * len(button_texts)
            button_spacing = 10
            
            total_width = sum(button_widths) + (button_spacing * (len(button_texts) - 1))
            
            # Position centrée pour les boutons
            start_x = (WIDTH - total_width) // 2
            current_x = start_x
            
            # Créer les boutons centrés horizontalement
            self.buttons = {}
            for i, text in enumerate(button_texts):
                button_rect = pygame.Rect(current_x, MENU_Y, button_widths[i], button_heights[i])
                self.buttons[text] = button_rect
                current_x += button_widths[i] + button_spacing

        def draw(self, screen):
            for text, rect in self.buttons.items():
                pygame.draw.rect(screen, (200, 200, 200), rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 2)
                font = pygame.font.Font(None, 24)
                text_surf = font.render(text, True, (0, 0, 0))
                text_rect = text_surf.get_rect(center=rect.center)
                screen.blit(text_surf, text_rect)

        def get_action(self, x, y):
            for text, rect in self.buttons.items():
                if rect.collidepoint(x, y):
                    return text
            return None

    # Titre centré
    def draw_title(screen):
        font = pygame.font.Font(None, 36)
        title = font.render("Constructeur de Quadrant", True, (0, 0, 0))
        title_rect = title.get_rect(center=(WIDTH//2, GRID_Y - 30))
        screen.blit(title, title_rect)

    # Initialisation des objets
    quadrant = Quadrant()
    palette = Palette()
    menu = Menu()

    # Boucle principale
    running = True
    while running:
        # Afficher l'image de fond ou un fond blanc
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill((255, 255, 255))
        
        # Dessiner le titre
        draw_title(screen)
        
        # Dessiner une bordure autour de la grille
        grid_border = pygame.Rect(GRID_X - 2, GRID_Y - 2, GRID_WIDTH + 4, GRID_HEIGHT + 4)
        pygame.draw.rect(screen, (0, 0, 0), grid_border, 2)
        
        quadrant.draw(screen)
        palette.draw(screen)
        menu.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if y < MENU_Y:
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