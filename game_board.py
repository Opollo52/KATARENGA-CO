import pygame
import numpy as np
import os
import sys
from config_manager import initialize_quadrants
from pawn import get_valid_moves, highlight_possible_moves, is_valid_move
from game_modes import GLOBAL_SELECTED_GAME, GLOBAL_SELECTED_OPPONENT
from congress import check_victory, highlight_connected_pawns, display_victory_message

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

def initialize_pawns_for_game_mode(game_mode):
    """
    Initialise les pions selon le mode de jeu sélectionné
    game_mode: 0 pour Katarenga, 1 pour Congress, 2 pour Isolation
    Retourne: une grille 8x8 avec les positions initiales des pions
    """
    # Créer une grille 8x8 vide pour les pions
    pawn_grid = np.zeros((8, 8), dtype=int)
    
    if game_mode == 0:  # Katarenga
        # Pions rouges sur la première ligne
        for col in range(8):
            pawn_grid[0][col] = 1
        
        # Pions bleus sur la dernière ligne
        for col in range(8):
            pawn_grid[7][col] = 2
    
    elif game_mode == 1:  # Congress
        # 8 pions de chaque couleur sur les bords
        # Positions des pions rouges (joueur 1) - 8 pions sur les bords
        red_positions = [
            (0, 1), (0, 4), (1, 7), (3, 0),  # Haut
            (4, 7), (6, 0), (7, 3), (7, 6)   # Bas
        ]
        
        # Positions des pions bleus (joueur 2) - 8 pions sur les bords
        blue_positions = [
            (0, 3), (0, 6), (1, 0), (3, 7),  # Haut
            (4, 0), (6, 7), (7, 1), (7, 4)   # Bas
        ]
        
        # Placer les pions rouges
        for row, col in red_positions:
            pawn_grid[row][col] = 1
        
        # Placer les pions bleus
        for row, col in blue_positions:
            pawn_grid[row][col] = 2
    
    elif game_mode == 2:  # Isolation
        # Pour Isolation, les pions commencent sur la bordure
        # Le jeu gérera leur placement sur le plateau
        pass
    
    return pawn_grid

def start_game(screen, quadrants_data):
    """Lance le jeu avec les quadrants sélectionnés"""
    # Sauvegarder la taille originale
    original_size = screen.get_size()
    
    # Configuration initiale pour le mode fenêtré avec bordures
    # Taille de fenêtre par défaut (peut être changée par l'utilisateur)
    window_width, window_height = 1024, 768
    pygame.display.set_caption("Partie en cours")
    
    # Variable pour suivre si on est en plein écran
    fullscreen = False
    
    # Couleurs
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (150, 150, 150)
    BLUE = (0, 0, 250)
    GREEN = (0, 200, 0)
    DARK_BLUE = (0, 0, 150)   # Couleur pour les pions bleus
    DARK_RED = (200, 0, 0)    # Couleur pour les pions rouges
    
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
    
    # Variables pour la gestion du jeu
    selected_pawn = None  # Position (row, col) du pion sélectionné
    possible_moves = []   # Liste des mouvements possibles pour le pion sélectionné
    current_player = 1    # Joueur actuel (1 = rouge/noir, 2 = bleu/blanc)
    game_over = False     # Indique si la partie est terminée
    winner = 0            # Joueur gagnant (0 = aucun, 1 = rouge, 2 = bleu)
    connected_pawns = []  # Liste des pions connectés du gagnant (pour Congress)
    
    # Importer dynamiquement la variable globale pour le mode de jeu
    # Cette importation répétée permettra de détecter les changements
    from game_modes import GLOBAL_SELECTED_GAME
    
    # Obtenir le mode de jeu actuel depuis la variable globale
    current_game_mode = GLOBAL_SELECTED_GAME
    
    # Initialiser les pions selon le mode de jeu
    pawn_grid = initialize_pawns_for_game_mode(current_game_mode)
    
    # Initialiser la phase de jeu
    game_phase = "play"
    if current_game_mode == 2:  # Isolation
        game_phase = "setup"
    
    # Initialiser les pions à placer pour le mode Isolation
    pions_a_placer = {1: 8, 2: 8} if current_game_mode == 2 else None
    
    # Fonction pour réinitialiser le plateau selon le mode de jeu actuel
    def reset_game_for_mode():
        nonlocal current_player, selected_pawn, possible_moves, game_over, game_phase, winner, connected_pawns
        
        # Obtenir le mode de jeu actuel depuis la variable globale
        from game_modes import GLOBAL_SELECTED_GAME
        current_game_mode = GLOBAL_SELECTED_GAME
        
        # Initialiser les pions selon le mode de jeu
        new_pawn_grid = initialize_pawns_for_game_mode(current_game_mode)
        
        # Réinitialiser les variables de jeu
        selected_pawn = None
        possible_moves = []
        current_player = 1
        game_over = False
        winner = 0
        connected_pawns = []
        
        # Spécificités pour le mode Isolation
        game_phase = "play"  # Par défaut "play" pour les modes standards
        new_pions_a_placer = None
        
        if current_game_mode == 2:  # Isolation
            game_phase = "setup"
            # Nombre de pions à placer pour chaque joueur
            new_pions_a_placer = {1: 8, 2: 8}  # 8 pions par joueur
        
        return current_game_mode, new_pawn_grid, new_pions_a_placer
    
    # Font standard pour les boutons et textes
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
    
    # Variable pour stocker le dernier mode de jeu connu
    last_known_game_mode = current_game_mode
    
    running = True
    while running:
        # Vérifier si le mode de jeu a changé
        from game_modes import GLOBAL_SELECTED_GAME
        if GLOBAL_SELECTED_GAME != last_known_game_mode:
            current_game_mode, new_pawn_grid, new_pions_a_placer = reset_game_for_mode()
            pawn_grid = new_pawn_grid
            if new_pions_a_placer:
                pions_a_placer = new_pions_a_placer
            last_known_game_mode = current_game_mode
        
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
                
                # Dessiner les pions s'il y en a sur cette case
                if pawn_grid[row][col] > 0:
                    pawn_color = DARK_RED if pawn_grid[row][col] == 1 else DARK_BLUE
                    pawn_radius = cell_size // 3
                    pawn_center = (
                        cell_rect.centerx,
                        cell_rect.centery
                    )
                    
                    # Mettre en évidence le pion sélectionné
                    if selected_pawn and selected_pawn == (row, col):
                        # Dessiner un cercle de sélection
                        highlight_radius = pawn_radius + 4
                        pygame.draw.circle(screen, (255, 255, 0), pawn_center, highlight_radius, 3)
                    
                    # Dessiner le pion (cercle plein avec bordure)
                    pygame.draw.circle(screen, pawn_color, pawn_center, pawn_radius)
                    pygame.draw.circle(screen, BLACK, pawn_center, pawn_radius, 2)
        
        # Dessiner la surbrillance des mouvements possibles si un pion est sélectionné
        if selected_pawn and possible_moves and not game_over:
            highlight_possible_moves(screen, possible_moves, board_x, board_y, cell_size)
        
        # Mettre en surbrillance les pions connectés si le jeu est terminé en mode Congress
        if game_over and winner > 0 and current_game_mode == 1:
            player_color = DARK_RED if winner == 1 else DARK_BLUE
            highlight_connected_pawns(screen, connected_pawns, board_x, board_y, cell_size, player_color)
            display_victory_message(screen, winner)
        
        # Afficher le joueur actuel sauf si le jeu est terminé
        if not game_over:
            player_text = font.render(f"Tour du joueur: {'Rouge' if current_player == 1 else 'Bleu'}", True, DARK_RED if current_player == 1 else DARK_BLUE)
            screen.blit(player_text, (current_width - 200, 20))
        
        # Afficher des informations spécifiques au mode de jeu
        mode_names = ["Katarenga", "Congress", "Isolation"]
        mode_text = font.render(f"Mode: {mode_names[current_game_mode]}", True, BLACK)
        screen.blit(mode_text, (current_width - 200, 50))
        
        # Afficher des informations spécifiques au mode Isolation (phase de configuration)
        if current_game_mode == 2 and game_phase == "setup":
            setup_text = font.render(f"Phase de placement - Pions à placer: {pions_a_placer[current_player]}", True, DARK_RED if current_player == 1 else DARK_BLUE)
            screen.blit(setup_text, (current_width // 2 - 150, 20))
        
        # Dessiner le bouton retour
        pygame.draw.rect(screen, BLUE, back_button)
        back_text = font.render("Retour", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, back_text_rect)
        
        # Traitement des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return_to_previous()
                return
                
            elif event.type == pygame.KEYDOWN:
                # Permettre de quitter avec la touche Échap
                if event.key == pygame.K_ESCAPE:
                    return_to_previous()
                    return
                
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                # Navigation
                if back_button.collidepoint(event.pos):
                    return_to_previous()
                    return
                elif fullscreen_button.collidepoint(event.pos):
                    toggle_fullscreen()
                
                # Gestion du jeu - clic sur le plateau
                mouse_x, mouse_y = event.pos
                # Vérifier si le clic est dans les limites du plateau
                if (board_x <= mouse_x < board_x + board_size and 
                    board_y <= mouse_y < board_y + board_size):
                    # Convertir les coordonnées du clic en indices de la grille
                    col = (mouse_x - board_x) // cell_size
                    row = (mouse_y - board_y) // cell_size
                    
                    # Mode Isolation - Phase de configuration
                    if current_game_mode == 2 and game_phase == "setup":
                        # Vérifier si la case est vide
                        if pawn_grid[row][col] == 0:
                            # Placer un pion du joueur actuel
                            pawn_grid[row][col] = current_player
                            
                            # Réduire le nombre de pions à placer
                            pions_a_placer[current_player] -= 1
                            
                            # Si le joueur a placé tous ses pions, passer au joueur suivant
                            if pions_a_placer[current_player] == 0:
                                current_player = 3 - current_player
                                
                                # Si tous les pions sont placés, passer à la phase de jeu
                                if pions_a_placer[current_player] == 0:
                                    game_phase = "play"
                    
                    # Mode normal ou Isolation en phase de jeu
                    elif game_phase == "play":
                        # Si un pion est déjà sélectionné
                        if selected_pawn:
                            selected_row, selected_col = selected_pawn
                            
                            # Vérifier si le clic est sur l'un des mouvements possibles
                            if (row, col) in possible_moves:
                                # Déplacer le pion
                                pawn_grid[row][col] = pawn_grid[selected_row][selected_col]
                                pawn_grid[selected_row][selected_col] = 0
                                
                                # Vérifier la condition de victoire pour le mode Congress
                                if current_game_mode == 1:  # Si mode Congress
                                    winner, connected_pawns = check_victory(pawn_grid)
                                    if winner > 0:
                                        game_over = True
                                
                                # Si le jeu n'est pas terminé, passer au joueur suivant
                                if not game_over:
                                    current_player = 3 - current_player  # Alterné entre 1 et 2
                                
                                # Réinitialiser la sélection
                                selected_pawn = None
                                possible_moves = []
                            
                            # Si le clic est sur un autre pion du même joueur
                            elif pawn_grid[row][col] == current_player:
                                # Sélectionner ce nouveau pion
                                selected_pawn = (row, col)
                                possible_moves = get_valid_moves(row, col, board_grid, pawn_grid)
                            
                            # Si le clic est ailleurs, annuler la sélection
                            else:
                                selected_pawn = None
                                possible_moves = []
                        
                        # Si aucun pion n'est sélectionné
                        else:
                            # Vérifier si le clic est sur un pion du joueur actuel
                            if pawn_grid[row][col] == current_player:
                                selected_pawn = (row, col)
                                possible_moves = get_valid_moves(row, col, board_grid, pawn_grid)
                
            elif event.type == pygame.VIDEORESIZE and not fullscreen:
                # Mettre à jour la taille de la fenêtre si l'utilisateur la redimensionne
                window_width, window_height = event.size
                screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
        
        pygame.display.flip()
    
    # Restaurer la taille d'écran originale avant de quitter
    return_to_previous()