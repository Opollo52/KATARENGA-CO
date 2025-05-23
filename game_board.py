import pygame
import os
import sys
import time
from pawn import get_valid_moves, highlight_possible_moves, is_valid_move
from game_modes import GLOBAL_SELECTED_GAME, GLOBAL_SELECTED_OPPONENT
from congress import check_victory, highlight_connected_pawns, display_victory_message

# Classe simple pour les animations de pions
class Animation:
    def __init__(self):
        self.moving_pawn = None
        self.move_start_time = 0
        self.move_duration = 0.8 
        self.start_pos = None
        self.end_pos = None
        self.moving_pawn_color = None  # Stocker la couleur du pion en mouvement
        self.pending_move = None  # Stocker le mouvement à exécuter après l'animation
        
    def start_move(self, start_row, start_col, end_row, end_col, board_x, board_y, cell_size, pawn_color):
        """Démarre une animation de déplacement"""
        self.moving_pawn = (start_row, start_col, end_row, end_col)
        self.moving_pawn_color = pawn_color  # Sauvegarder la couleur
        self.move_start_time = time.time()
        
        # Positions d'écran
        self.start_pos = (
            board_x + start_col * cell_size + cell_size // 2,
            board_y + start_row * cell_size + cell_size // 2
        )
        self.end_pos = (
            board_x + end_col * cell_size + cell_size // 2,
            board_y + end_row * cell_size + cell_size // 2
        )
    
    def get_current_pos(self):
        """Retourne la position actuelle du pion en mouvement"""
        if not self.moving_pawn:
            return None
            
        elapsed = time.time() - self.move_start_time
        progress = min(elapsed / self.move_duration, 1.0)
        
        # Easing simple (ease-out)
        progress = 1 - (1 - progress) ** 3
        
        current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress
        
        if progress >= 1.0:
            self.moving_pawn = None
            self.moving_pawn_color = None  # Réinitialiser la couleur
            # Marquer que l'animation est terminée mais ne pas réinitialiser pending_move ici
            
        return (int(current_x), int(current_y))
    
    def is_moving(self):
        """Vérifie si une animation est en cours"""
        return self.moving_pawn is not None

    def has_pending_move(self):
        """Vérifie s'il y a un mouvement en attente à exécuter"""
        return self.pending_move is not None
    
    def execute_pending_move(self, pawn_grid, current_game_mode):
        """Exécute le mouvement en attente et retourne les infos de victoire"""
        if not self.pending_move:
            return None, None, None
            
        from_pos = self.pending_move['from']
        to_pos = self.pending_move['to']
        
        # Exécuter le mouvement dans la grille logique
        pawn_grid[to_pos[0]][to_pos[1]] = pawn_grid[from_pos[0]][from_pos[1]]
        pawn_grid[from_pos[0]][from_pos[1]] = 0
        
        # Vérifier la condition de victoire pour le mode Congress
        winner = 0
        connected_pawns = []
        game_over = False
        
        if current_game_mode == 1:  # Si mode Congress
            winner, connected_pawns = check_victory(pawn_grid)
            if winner > 0:
                game_over = True
        
        # Nettoyer le mouvement en attente
        self.pending_move = None
        
        return winner, connected_pawns, game_over

def draw_animated_pawns(screen, pawn_grid, board_x, board_y, cell_size, selected_pawn, animation):
    """Dessine les pions avec animations simples"""
    DARK_RED = (200, 0, 0)
    DARK_BLUE = (0, 0, 150)
    BLACK = (0, 0, 0)
    
    # Obtenir la position du pion en mouvement
    moving_pos = animation.get_current_pos()
    moving_pawn_info = animation.moving_pawn
    
    for row in range(8):
        for col in range(8):
            if pawn_grid[row][col] > 0:
                # Skip le pion en mouvement (on le dessine séparément)
                if (moving_pawn_info and 
                    moving_pawn_info[0] == row and moving_pawn_info[1] == col):
                    continue
                
                pawn_color = DARK_RED if pawn_grid[row][col] == 1 else DARK_BLUE
                
                # Position normale du pion
                pawn_center = (
                    board_x + col * cell_size + cell_size // 2,
                    board_y + row * cell_size + cell_size // 2
                )
                
                # Rayon normal
                radius = cell_size // 3
                
                # Cercle de sélection jaune si pion sélectionné
                if selected_pawn and selected_pawn == (row, col):
                    highlight_radius = radius + 4
                    pygame.draw.circle(screen, (255, 255, 0), pawn_center, highlight_radius, 3)
                
                # Dessiner le pion
                pygame.draw.circle(screen, pawn_color, pawn_center, radius)
                pygame.draw.circle(screen, BLACK, pawn_center, radius, 2)
    
    # Dessiner le pion en mouvement par-dessus tout
    if moving_pos and moving_pawn_info and animation.moving_pawn_color:
        # Utiliser la couleur sauvegardée
        pawn_color = DARK_RED if animation.moving_pawn_color == 1 else DARK_BLUE
        radius = cell_size // 3
        
        pygame.draw.circle(screen, pawn_color, moving_pos, radius)
        pygame.draw.circle(screen, BLACK, moving_pos, radius, 2)

def create_game_board(quadrant_grid_data):
    """
    Crée un plateau de jeu à partir des données de grille des 4 quadrants
    """
    # Créer une grille 8x8 vide pour le plateau (utilise des listes au lieu de numpy)
    board_grid = [[0 for _ in range(8)] for _ in range(8)]
    
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
    """
    # Créer une grille 8x8 vide pour les pions (utilise des listes au lieu de numpy)
    pawn_grid = [[0 for _ in range(8)] for _ in range(8)]
    
    if game_mode == 0:  # Katarenga
        # Pions rouges sur la première ligne
        for col in range(8):
            pawn_grid[0][col] = 1
        
        # Pions bleus sur la dernière ligne
        for col in range(8):
            pawn_grid[7][col] = 2
    
    elif game_mode == 1:  # Congress
        # Positions des pions rouges (joueur 1)
        red_positions = [
            (0, 1), (0, 4), (1, 7), (3, 0), 
            (4, 7), (6, 0), (7, 3), (7, 6)   
        ]
        
        # Positions des pions bleus (joueur 2) 
        blue_positions = [
            (0, 3), (0, 6), (1, 0), (3, 7), 
            (4, 0), (6, 7), (7, 1), (7, 4) 
        ]
        
        # Placer les pions rouges
        for row, col in red_positions:
            pawn_grid[row][col] = 1
        
        # Placer les pions bleus
        for row, col in blue_positions:
            pawn_grid[row][col] = 2
    
    elif game_mode == 2:  # Isolation
        pass
    return pawn_grid

def start_game(screen, quadrants_data):
    """
    Lance le jeu avec les quadrants sélectionnés
    """
    pygame.display.set_caption("Partie en cours")

    # Couleurs
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    background_image = pygame.image.load(os.path.join(script_dir, "img", "fond.png"))
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (150, 150, 150)
    BLUE = (0, 0, 250)
    GREEN = (0, 200, 0)
    DARK_BLUE = (0, 0, 150)   
    DARK_RED = (200, 0, 0) 
    
    # Chargement des images
    PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # Dictionnaire des valeurs de cellule aux images
    images = {}
    images[1] = pygame.image.load(os.path.join(PATH, "img/yellow.png"))  
    images[2] = pygame.image.load(os.path.join(PATH, "img/green.png"))  
    images[3] = pygame.image.load(os.path.join(PATH, "img/blue.png"))   
    images[4] = pygame.image.load(os.path.join(PATH, "img/red.png"))   
    
    # Chargement de l'image du cadre
    frame_image = pygame.image.load(os.path.join(PATH, "img/frame.png"))
    
    # Créer le plateau de jeu à partir des données des quadrants
    board_grid = create_game_board(quadrants_data)
    
    # Créer l'instance d'animation
    animation = Animation()
    
    # Variables pour la gestion du jeu
    selected_pawn = None 
    possible_moves = []  
    current_player = 1  
    game_over = False
    winner = 0         
    connected_pawns = [] 
    
    # Pour detecter les changements de mode de jeu 
    from game_modes import GLOBAL_SELECTED_GAME
    
    # Obtenir le mode de jeu actuel depuis la variable globale
    current_game_mode = GLOBAL_SELECTED_GAME
    
    # Initialiser les pions selon le mode de jeu
    pawn_grid = initialize_pawns_for_game_mode(current_game_mode)
    
    # Initialiser la phase de jeu
    game_phase = "play"
    
    # Fonction pour réinitialiser le plateau selon le mode de jeu actuel
    def reset_game_for_mode():
        nonlocal current_player, selected_pawn, possible_moves, game_over, game_phase, winner, connected_pawns
        
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

    # Font standard pour les boutons et textes
    font = pygame.font.Font(None, 24)
    # Fonction pour retourner à l'écran précédent
    def return_to_previous():
        return
    
    # Variable pour stocker le dernier mode de jeu connu
    last_known_game_mode = current_game_mode
    
    # Horloge pour contrôler le framerate
    clock = pygame.time.Clock()
    
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
        
        # Taille du plateau en pixels 
        board_size = 8 * cell_size
        
        # Position du plateau avec espace pour le contour
        board_x = (current_width - board_size) // 2
        board_y = (current_height - board_size) // 2
        
        # Zone complète du plateau avec contour
        board_rect = pygame.Rect(
            board_x - cell_size, 
            board_y - cell_size,
            board_size + 2 * cell_size,
            board_size + 2 * cell_size
        )
        
        # Boutons
        back_button = pygame.Rect(20, 20, 80, 30)
        
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))        
        # Dessiner le contour du plateau
        if frame_image:
            # Redimensionner le cadre à la taille du plateau avec bordure
            scaled_frame = pygame.transform.scale(frame_image, (
                board_size + 2 * cell_size,
                board_size + 2 * cell_size
            ))
            screen.blit(scaled_frame, (board_x - cell_size, board_y - cell_size))
        
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
                
                # Toujours dessiner une bordure
                pygame.draw.rect(screen, BLACK, cell_rect, 2)
        
        # Dessiner les pions avec animations
        draw_animated_pawns(screen, pawn_grid, board_x, board_y, cell_size, selected_pawn, animation)
        
        # Vérifier si l'animation est terminée et exécuter le mouvement en attente
        if not animation.is_moving() and animation.has_pending_move():
            winner_result, connected_result, game_over_result = animation.execute_pending_move(pawn_grid, current_game_mode)
            if winner_result is not None:
                winner = winner_result
                connected_pawns = connected_result
                game_over = game_over_result
            
            # Si le jeu n'est pas terminé, passer au joueur suivant
            if not game_over:
                current_player = 3 - current_player  # Alterné entre 1 et 2
        
        # Dessiner les mouvements possibles
        if selected_pawn and possible_moves and not game_over and not animation.is_moving():
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
                # Quitter avec la touche Échap
                if event.key == pygame.K_ESCAPE:
                    return_to_previous()
                    return
                
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and not animation.is_moving():
                # Quitter bouton retour
                if back_button.collidepoint(event.pos):
                    return_to_previous()
                    return
                
                # clic sur le plateau
                mouse_x, mouse_y = event.pos
                # Si le clic est dans les limites du plateau
                if (board_x <= mouse_x < board_x + board_size and 
                    board_y <= mouse_y < board_y + board_size):
                    # Convertir les coordonnées du clic en indices de la grille
                    col = (mouse_x - board_x) // cell_size
                    row = (mouse_y - board_y) // cell_size
                    
                    if game_phase == "play":
                        # Si un pion est déjà sélectionné
                        if selected_pawn:
                            selected_row, selected_col = selected_pawn
                            
                            # Vérifier si le clic est sur l'un des mouvements possibles
                            if (row, col) in possible_moves:
                                # Démarrer l'animation AVEC la couleur du pion
                                animation.start_move(selected_row, selected_col, row, col, board_x, board_y, cell_size, pawn_grid[selected_row][selected_col])
                                
                                # Stocker le mouvement pour l'exécuter après l'animation
                                animation.pending_move = {
                                    'from': (selected_row, selected_col),
                                    'to': (row, col),
                                    'pawn_color': pawn_grid[selected_row][selected_col]
                                }
                                
                                # Réinitialiser la sélection immédiatement
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
                
        pygame.display.flip()
        clock.tick(60)  # 60 FPS pour des animations fluides