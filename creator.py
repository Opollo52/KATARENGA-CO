import pygame
import os
import sys

def show_creator(screen):
    # Initialisation de Pygame
    pygame.init()

    # Définition des constantes
    WIDTH, HEIGHT = 675, 500
    GRID_SIZE = 4
    CELL_SIZE = 100
    PALETTE_X = WIDTH - (CELL_SIZE * 1.5)
    MENU_Y = HEIGHT - 50  # Position du menu

    # Liste des couleurs et des images associées
    COLOR_TO_IMAGE = {
        (250, 250, 0): "img/yellow.png",
        (0, 0, 250): "img/blue.png",
        (0, 250, 0): "img/green.png",
        (250, 0, 0): "img/red.png"
    }

    # Chemin du dossier contenant les images
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    SAVE_DIR = os.path.join(SCRIPT_DIR, "quadrant")
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Chargement des images (si elles existent)
    images = {}
    for color, filename in COLOR_TO_IMAGE.items():
        img_path = os.path.join(SCRIPT_DIR, filename)
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)
            images[color] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        else:
            print(f"Image {filename} introuvable, la couleur {color} sera utilisée.")

    # Création de la fenêtre
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
            self.grid = [[(255, 255, 255) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        def save(self):
            existing_files = len([f for f in os.listdir(SAVE_DIR) if f.startswith("quadrant_")])
            filename = os.path.join(SAVE_DIR, f"quadrant_{existing_files + 1}.png")
            quadrant_surface = pygame.Surface((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
            quadrant_surface.fill((255, 255, 255))

            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    color = self.grid[row][col]
                    if color in images:
                        quadrant_surface.blit(images[color], (col * CELL_SIZE, row * CELL_SIZE))
                    else:
                        pygame.draw.rect(quadrant_surface, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(quadrant_surface, (0, 0, 0), (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)

            pygame.image.save(quadrant_surface, filename)
            print(f"Grille sauvegardée sous {filename}")

    class Palette:
        def __init__(self):
            self.colors = list(COLOR_TO_IMAGE.keys())
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

    pygame.quit()

def run_creator(screen):
    show_creator(screen)
