import pygame
import numpy as np
import os
import sys
from config_manager import initialize_quadrants

def create_game_board(quadrant_grid_data):
    """
    Crée un plateau de jeu à partir des données de grille des 4 quadrants
    quadrant_grid_data: liste de 4 grilles 4x4 représentant les quadrants
    Retourne: une grille 8x8 pour le plateau complet
    """
    # Créer une grille 8x8 vide
    board_grid = np.zeros((8, 8), dtype=int)
    
    # Remplir la grille avec les données des quadrants
    if len(quadrant_grid_data) == 4:
        # Quadrant 1 (haut gauche)
        for i in range(4):
            for j in range(4):
                if i < len(quadrant_grid_data[0]) and j < len(quadrant_grid_data[0][i]):
                    board_grid[i][j] = quadrant_grid_data[0][i][j]
                    
        # Quadrant 2 (haut droite)
        for i in range(4):
            for j in range(4):
                if i < len(quadrant_grid_data[1]) and j < len(quadrant_grid_data[1][i]):
                    board_grid[i][j+4] = quadrant_grid_data[1][i][j]
                    
        # Quadrant 3 (bas gauche)
        for i in range(4):
            for j in range(4):
                if i < len(quadrant_grid_data[2]) and j < len(quadrant_grid_data[2][i]):
                    board_grid[i+4][j] = quadrant_grid_data[2][i][j]
                    
        # Quadrant 4 (bas droite)
        for i in range(4):
            for j in range(4):
                if i < len(quadrant_grid_data[3]) and j < len(quadrant_grid_data[3][i]):
                    board_grid[i+4][j+4] = quadrant_grid_data[3][i][j]
    
    return board_grid

def start_game(screen, quadrants_data):
    """Lance le jeu avec les quadrants sélectionnés"""
    # Sauvegarder la taille originale
    original_size = screen.get_size()
    
    # Configuration initiale pour le mode fenêtré avec bordures
    # Taille de fenêtre par défaut (peut être changée par l'utilisateur)
    window_width, window_height = 1024, 768
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
    pygame.display.set_caption("Partie en cours")
    
    # Variable pour suivre si on est en plein écran
    fullscreen = False
    
    # Couleurs
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (150, 150, 150)
    BLUE = (0, 0, 250)
    GREEN = (0, 200, 0)
    
    # Chargement des images
    SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # Dictionnaire des valeurs de cellule aux images
    images = {}
    try:
        images[1] = pygame.image.load(os.path.join(SCRIPT_DIR, "img/yellow.png"))  # Jaune → 1
        images[2] = pygame.image.load(os.path.join(SCRIPT_DIR, "img/green.png"))   # Vert → 2
        images[3] = pygame.image.load(os.path.join(SCRIPT_DIR, "img/blue.png"))    # Bleu → 3
        images[4] = pygame.image.load(os.path.join(SCRIPT_DIR, "img/red.png"))     # Rouge → 4
        
        # Charger l'image du cadre ornemental
        frame_image = pygame.image.load(os.path.join(SCRIPT_DIR, "img/frame.png"))
    except pygame.error as e:
        print(f"Erreur lors du chargement des images: {e}")
        print("Vérifiez le dossier img/")
        frame_image = None
    
    # Créer le plateau de jeu à partir des données des quadrants
    board_grid = create_game_board(quadrants_data)
    
    # Font standard pour les boutons
    font = pygame.font.Font(None, 24)
    
    # Fonction pour basculer entre plein écran et fenêtré
    def toggle_fullscreen():
        nonlocal fullscreen, screen
        if fullscreen:
            # Revenir au mode fenêtré
            screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
            fullscreen = False
        else:
            # Passer en plein écran
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            fullscreen = True
    
    # Fonction pour retourner à l'écran précédent
    def return_to_previous():
        pygame.display.set_mode(original_size)
        return
    
    running = True
    while running:
        # Récupérer les dimensions actuelles de la fenêtre
        current_width, current_height = screen.get_size()
        
        # Calculer la taille des cellules en fonction de la hauteur de l'écran
        cell_size = min(current_width, current_height) // 12
        
        # Redimensionner les images
        for key in images:
            images[key] = pygame.transform.scale(images[key], (cell_size, cell_size))
        
        # Taille du plateau en pixels (8 cellules)
        board_size = 8 * cell_size
        
        # La bordure a la même taille qu'une cellule
        border_size = cell_size
        corner_size = cell_size
        
        # Position du plateau (centré) avec espace pour le contour
        board_x = (current_width - board_size) // 2
        board_y = (current_height - board_size) // 2
        
        # Zone complète du plateau avec contour
        board_rect = pygame.Rect(
            board_x - border_size, 
            board_y - border_size,
            board_size + 2 * border_size,
            board_size + 2 * border_size
        )
        
        # Positions des coins pour les carrés gris (si le cadre ornemental n'est pas disponible)
        corners = [
            (board_rect.left, board_rect.top),                      # Coin supérieur gauche
            (board_rect.right - corner_size, board_rect.top),       # Coin supérieur droit
            (board_rect.left, board_rect.bottom - corner_size),     # Coin inférieur gauche
            (board_rect.right - corner_size, board_rect.bottom - corner_size)  # Coin inférieur droit
        ]
        
        # Boutons
        back_button = pygame.Rect(20, 20, 80, 30)
        fullscreen_button = pygame.Rect(120, 20, 140, 30)
        
        screen.fill(WHITE)
        
        # Dessiner le contour du plateau
        if frame_image:
            # Redimensionner le cadre à la taille du plateau avec bordure
            scaled_frame = pygame.transform.scale(frame_image, (
                board_size + 2 * border_size,
                board_size + 2 * border_size
            ))
            screen.blit(scaled_frame, (board_x - border_size, board_y - border_size))
        else:
            # Fallback: dessiner le contour noir basique si l'image n'est pas disponible
            pygame.draw.rect(screen, BLACK, board_rect)
            
            # Dessiner les carrés gris dans les coins
            for corner_pos in corners:
                corner_rect = pygame.Rect(corner_pos[0], corner_pos[1], corner_size, corner_size)
                pygame.draw.rect(screen, GRAY, corner_rect)
                pygame.draw.rect(screen, BLACK, corner_rect, 1)  # Petite bordure noire
        
        # Dessiner le plateau
        for row in range(8):
            for col in range(8):
                cell_value = board_grid[row][col]
                
                cell_rect = pygame.Rect(
                    board_x + col * cell_size,
                    board_y + row * cell_size,
                    cell_size,
                    cell_size
                )
                
                # Dessiner la cellule avec l'image correspondante
                if cell_value in images:
                    screen.blit(images[cell_value], cell_rect)
                else:
                    # Si pas d'image (valeur 0), utiliser couleur blanche
                    pygame.draw.rect(screen, WHITE, cell_rect)
                
                # Toujours dessiner une bordure
                pygame.draw.rect(screen, BLACK, cell_rect, 2)
        
        # Dessiner le bouton retour
        pygame.draw.rect(screen, BLUE, back_button)
        back_text = font.render("Retour", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, back_text_rect)
        
        # Dessiner le bouton plein écran
        pygame.draw.rect(screen, GREEN, fullscreen_button)
        fs_text = font.render("Plein écran" if not fullscreen else "Fenêtré", True, WHITE)
        fs_text_rect = fs_text.get_rect(center=fullscreen_button.center)
        screen.blit(fs_text, fs_text_rect)
        
        # Traitement des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return_to_previous()
                return
                
            elif event.type == pygame.KEYDOWN:
                # Permettre de quitter avec la touche Échap
                if event.key == pygame.K_ESCAPE:
                    if fullscreen:
                        # Si en plein écran, revenir au mode fenêtré
                        toggle_fullscreen()
                    else:
                        # Si déjà en fenêtré, retourner à l'écran précédent
                        return_to_previous()
                        return
                
                # Touche F11 pour basculer entre plein écran et fenêtré
                elif event.key == pygame.K_F11:
                    toggle_fullscreen()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return_to_previous()
                    return
                elif fullscreen_button.collidepoint(event.pos):
                    toggle_fullscreen()
                    
            elif event.type == pygame.VIDEORESIZE and not fullscreen:
                # Mettre à jour la taille de la fenêtre si l'utilisateur la redimensionne
                window_width, window_height = event.size
                screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
        
        pygame.display.flip()
    
    # Restaurer la taille d'écran originale avant de quitter
    return_to_previous()