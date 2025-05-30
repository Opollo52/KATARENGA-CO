import pygame
import os
import sys
import time
import random
from assets.colors import Colors
from pawn import get_valid_moves, highlight_possible_moves, is_valid_move
from game_modes import GLOBAL_SELECTED_GAME, GLOBAL_SELECTED_OPPONENT
from congress import check_victory, highlight_connected_pawns
from isolation import place_pawn, check_isolation_victory
from katarenga import check_minimum_pawn_victory_condition


def get_valid_moves_with_mode(row, col, board_grid, pawn_grid, game_mode):
    """
    Version locale de get_valid_moves qui utilise maintenant pawn.py pour tout
    """
    from pawn import get_valid_moves
    return get_valid_moves(row, col, board_grid, pawn_grid, game_mode)

# Version améliorée de la classe Animation
class Animation:
    def __init__(self):
        self.moving_pawn = None
        self.move_start_time = 0
        self.move_duration = 0.8 
        self.start_pos = None
        self.end_pos = None
        self.moving_pawn_color = None  
        self.pending_move = None
        self.animation_finished = False
        
    def start_move(self, start_row, start_col, end_row, end_col, board_x, board_y, cell_size, pawn_color):
        """Démarre une animation de déplacement"""
        self.moving_pawn = (start_row, start_col, end_row, end_col)
        self.moving_pawn_color = pawn_color
        self.move_start_time = time.time()
        self.animation_finished = False
        
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
        progress = 1 - (1 - progress) ** 3  # Easing function
        
        current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress
        
        if progress >= 1.0 and not self.animation_finished:
            self.animation_finished = True
            
        return (int(current_x), int(current_y))
    
    def is_moving(self):
        """Vérifie si une animation est en cours"""
        return self.moving_pawn is not None and not self.animation_finished
    
    def is_animation_finished(self):
        """Vérifie si l'animation vient de se terminer"""
        return self.animation_finished
    
    def complete_animation(self):
        """Finalise l'animation"""
        self.moving_pawn = None
        self.moving_pawn_color = None
        self.animation_finished = False

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
        
        # Vérifier la condition de victoire selon le mode de jeu
        winner = 0
        connected_pawns = []
        game_over = False
        
        if current_game_mode == 1:  # Si mode Congress
            winner, connected_pawns = check_victory(pawn_grid)
            if winner > 0:
                game_over = True
        elif current_game_mode == 2:  # Si mode Isolation
            game_over, winner = check_isolation_victory(pawn_grid, self.pending_move['pawn_color'], None)
        elif current_game_mode == 0:  # Si mode Katarenga
            from katarenga import check_katarenga_victory
            winner = check_katarenga_victory()
            if winner > 0:
                game_over = True
        
        # Nettoyer le mouvement en attente
        self.pending_move = None
        
        return winner, connected_pawns, game_over

def draw_animated_pawns(screen, pawn_grid, board_x, board_y, cell_size, selected_pawn, animation, current_game_mode):
    """Dessine les pions avec animations simples"""
    DARK_RED = Colors.DARK_RED
    DARK_BLUE = Colors.DARK_BLUE
    BLACK = Colors.BLACK
    
    # Obtenir la position du pion en mouvement
    moving_pos = animation.get_current_pos()
    moving_pawn_info = animation.moving_pawn
    
    # Déterminer la taille de la grille selon le mode
    grid_size = 10 if current_game_mode == 0 else 10  # Toujours 10x10 maintenant
    
    for row in range(grid_size):
        for col in range(grid_size):
            if pawn_grid[row][col] > 0:
                # Skip le pion en mouvement à sa position D'ORIGINE
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
        pawn_color = DARK_RED if animation.moving_pawn_color == 1 else DARK_BLUE
        radius = cell_size // 3
        
        pygame.draw.circle(screen, pawn_color, moving_pos, radius)
        pygame.draw.circle(screen, BLACK, moving_pos, radius, 2)

def show_invalid_positions_isolation(screen, pawn_grid, board_grid, board_x, board_y, cell_size):
    """
    Affiche des croix sur les cases où il n'est pas possible de placer un pion
    en utilisant directement les fonctions d'isolation.py
    """
    from isolation import is_position_safe
    
    for row in range(1, 9):  # Seulement la zone de jeu 8x8
        for col in range(1, 9):
            # Si la case est vide mais pas sûre
            if pawn_grid[row][col] == 0 and not is_position_safe(pawn_grid, row, col, board_grid):
                # Dessiner une croix rouge
                x = board_x + col * cell_size
                y = board_y + row * cell_size
                
                # Marges pour la croix
                margin = cell_size // 4
                
                # Dessiner la croix noir
                pygame.draw.line(screen, (0, 0, 0), 
                            (x + margin, y + margin), 
                            (x + cell_size - margin, y + cell_size - margin), 8)
                pygame.draw.line(screen, (0, 0, 0), 
                            (x + cell_size - margin, y + margin), 
                            (x + margin, y + cell_size - margin), 8)

def create_game_board(quadrant_grid_data):
    """
    Crée un plateau de jeu à partir des données de grille des 4 quadrants
    """
    # Créer une grille 10x10 vide pour le plateau
    board_grid = [[0 for _ in range(10)] for _ in range(10)]
    
    # Remplir la grille avec les données des quadrants
    if len(quadrant_grid_data) == 4:
        # Quadrant 1 (haut gauche)
        for i in range(4):
            for j in range(4):
                board_grid[i + 1][j + 1] = quadrant_grid_data[0][i][j]

        # Quadrant 2 (haut droite)
        for i in range(4):
            for j in range(4):
                board_grid[i + 1][j + 5] = quadrant_grid_data[1][i][j]

        # Quadrant 3 (bas gauche)
        for i in range(4):
            for j in range(4):
                board_grid[i + 5][j + 1] = quadrant_grid_data[2][i][j]

        # Quadrant 4 (bas droite)
        for i in range(4):
            for j in range(4):
                board_grid[i + 5][j + 5] = quadrant_grid_data[3][i][j]
    
    return board_grid

def initialize_pawns_for_game_mode(game_mode):
    """
    Initialise les pions selon le mode de jeu sélectionné
    """
    # Créer une grille 10x10 vide pour les pions
    pawn_grid = [[0 for _ in range(10)] for _ in range(10)]
    
    if game_mode == 0:  # Katarenga
        # Pions rouges ligne 1 (joueur 1) - colonnes 1 à 8
        for col in range(1, 9):
            pawn_grid[1][col] = 1
        # Pions bleus ligne 8 (joueur 2) - colonnes 1 à 8
        for col in range(1, 9):
            pawn_grid[8][col] = 2

    elif game_mode == 1:  # Congress
        # Positions des pions rouges (joueur 1) - ajustées pour la zone 8x8
        red_positions = [
            (1, 2), (1, 5), (2, 8), (4, 1), 
            (5, 8), (7, 1), (8, 4), (8, 7)   
        ]
        
        # Positions des pions bleus (joueur 2) - ajustées pour la zone 8x8
        blue_positions = [
            (1, 4), (1, 7), (2, 1), (4, 8), 
            (5, 1), (7, 8), (8, 2), (8, 5) 
        ]
        
        # Placer les pions rouges
        for row, col in red_positions:
            pawn_grid[row][col] = 1
        
        # Placer les pions bleus
        for row, col in blue_positions:
            pawn_grid[row][col] = 2
    
    elif game_mode == 2:  # Isolation
        # Plateau vide au début pour le mode Isolation
        pass
    
    return pawn_grid

def start_game(screen, quadrants_data):
    """
    Lance le jeu avec les quadrants sélectionnés
    """
    pygame.display.set_caption("Partie en cours")

    # Couleurs
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    background_image = pygame.image.load(os.path.join(script_dir, "assets", "img", "fond.png"))
    
    WHITE = Colors.WHITE
    BLACK = Colors.BLACK
    GRAY = Colors.GRAY
    BLUE = Colors.BLUE
    RED = Colors.RED
    GREEN = Colors.GREEN
    DARK_BLUE = Colors.DARK_BLUE 
    DARK_RED = Colors.DARK_RED
    
    # Chargement des images
    PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # Dictionnaire des valeurs de cellule aux images
    images = {}
    images[1] = pygame.image.load(os.path.join(PATH, "assets", "img", "yellow.png"))  
    images[2] = pygame.image.load(os.path.join(PATH, "assets", "img", "green.png"))  
    images[3] = pygame.image.load(os.path.join(PATH, "assets", "img", "blue.png"))   
    images[4] = pygame.image.load(os.path.join(PATH, "assets", "img", "red.png"))

    # Chargement de l'image du cadre    
    frame_image = pygame.image.load(os.path.join(PATH, "assets", "img", "frame.png"))    
    
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
    
    # Obtenir le mode de jeu actuel depuis la variable globale
    from game_modes import GLOBAL_SELECTED_GAME
    current_game_mode = GLOBAL_SELECTED_GAME
    
    # Initialiser les pions selon le mode de jeu
    pawn_grid = initialize_pawns_for_game_mode(current_game_mode)
    
    # Initialiser Katarenga si nécessaire
    if current_game_mode == 0:
        from katarenga import reset_camps
        reset_camps()
    
    # Initialiser la phase de jeu
    game_phase = "play"
    
    def reset_game_for_mode():
        nonlocal current_player, selected_pawn, possible_moves, game_over, game_phase, winner, connected_pawns, current_game_mode

        current_game_mode = GLOBAL_SELECTED_GAME
        new_pawn_grid = initialize_pawns_for_game_mode(current_game_mode)
        
        # Réinitialiser Katarenga si nécessaire
        if current_game_mode == 0:
            from katarenga import reset_camps
            reset_camps()

        # Réinitialiser les variables de jeu
        selected_pawn = None
        possible_moves = []
        current_player = 1
        game_over = False
        winner = 0
        connected_pawns = []
        game_phase = "play"

        return new_pawn_grid
        
    # Font standard pour les boutons et textes
    font = pygame.font.Font(None, 24)
    
    # Variable pour stocker le dernier mode de jeu connu
    last_known_game_mode = current_game_mode
    
    # Horloge pour contrôler le framerate
    clock = pygame.time.Clock()
    
    running = True
    while running:
        # Vérifier si le mode de jeu a changé
        from game_modes import GLOBAL_SELECTED_GAME
        if GLOBAL_SELECTED_GAME != last_known_game_mode:
            current_game_mode = GLOBAL_SELECTED_GAME
            pawn_grid = reset_game_for_mode()
            last_known_game_mode = current_game_mode
        
        # Récupérer les dimensions actuelles de la fenêtre
        current_width, current_height = screen.get_size()
        
        if current_game_mode == 0:
            cell_size = min(current_width, current_height) // 10  # Taille agrandie pour le plateau
            frame_cell_size = min(current_width, current_height) // 12  # Garde le cadre plus petit
        else:
            cell_size = frame_cell_size = min(current_width, current_height) // 12


        
        # Redimensionner les images
        for key in images:
            images[key] = pygame.transform.scale(images[key], (cell_size, cell_size))
        
        # Taille du plateau en pixels 
        board_size = 10 * cell_size
        frame_board_size = 10 * frame_cell_size
        frame_x = (current_width - frame_board_size) // 2
        frame_y = (current_height - frame_board_size) // 2

        
        # Position du plateau avec espace pour le contour
        board_x = (current_width - board_size) // 2
        board_y = (current_height - board_size) // 2
        
        # Boutons
        back_button = pygame.Rect(20, 20, 80, 30)
        
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))        
        
        frame_board_size = 10 * frame_cell_size

        # Dessiner le contour du plateau
        if frame_image:
            scaled_frame = pygame.transform.scale(frame_image, (
                frame_board_size + 2 * frame_cell_size,
                frame_board_size + 2 * frame_cell_size
            ))
            screen.blit(scaled_frame, (frame_x - frame_cell_size, frame_y - frame_cell_size))


        
        # Dessiner le plateau selon le mode
        if current_game_mode == 0:  # Katarenga - plateau 10x10
            for row in range(10):
                for col in range(10):
                    cell_rect = pygame.Rect(
                        board_x + col * cell_size,
                        board_y + row * cell_size,
                        cell_size,
                        cell_size
                    )
                    
                    # Les camps sont aux coins
                    if (row == 0 and col == 0) or (row == 0 and col == 9) or (row == 9 and col == 0) or (row == 9 and col == 9):
                        # Les camps seront dessinés séparément, ne pas dessiner de bordure ici
                        pass
                    elif 1 <= row <= 8 and 1 <= col <= 8:
                        # Zone de jeu normale - dessiner seulement si on a une texture
                        cell_value = board_grid[row][col]
                        if cell_value in images:
                            screen.blit(images[cell_value], cell_rect)
                            # Dessiner la bordure seulement sur les cases avec texture
                            pygame.draw.rect(screen, BLACK, cell_rect, 2)
                    # Ne pas dessiner les cases vides des bords (lignes/colonnes 0 et 9)
            
            # Dessiner les camps pour Katarenga
            from katarenga import draw_camps
            draw_camps(screen, board_x, board_y, cell_size)
        
        else:  # Congress et Isolation - afficher seulement 8x8
            for row in range(1, 9):
                for col in range(1, 9):
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
                        # Dessiner la bordure seulement sur les cases avec texture
                        pygame.draw.rect(screen, BLACK, cell_rect, 2)
        
        # Dessiner les pions avec animations
        draw_animated_pawns(screen, pawn_grid, board_x, board_y, cell_size, selected_pawn, animation, current_game_mode)
        
        # Afficher les positions invalides pour Isolation
        if current_game_mode == 2 and not game_over and not animation.is_moving():
            show_invalid_positions_isolation(screen, pawn_grid, board_grid, board_x, board_y, cell_size)
        
        # Gestion spéciale Katarenga : entrée dans les camps
        if current_game_mode == 0 and not animation.is_moving() and animation.has_pending_move():
            from katarenga import place_in_camp, check_katarenga_victory, get_camp_positions
            to_row, to_col = animation.pending_move['to']
            player = animation.pending_move['pawn_color']
            camp_positions = get_camp_positions(player)
            
            if (to_row, to_col) in camp_positions:
                if place_in_camp(to_row, to_col, pawn_grid, player):
                    pawn_grid[animation.pending_move['from'][0]][animation.pending_move['from'][1]] = 0
                    animation.pending_move = None
                    winner = check_katarenga_victory()
                    game_over = winner > 0
                    if not game_over:
                        current_player = 3 - current_player
                    animation.complete_animation()
                    continue

        if not animation.is_moving() and animation.has_pending_move():
            winner_result, connected_result, game_over_result = animation.execute_pending_move(pawn_grid, current_game_mode)
            
            if winner_result is not None:
                winner = winner_result
                connected_pawns = connected_result
                game_over = game_over_result

            # 💡 Vérifier si un joueur n’a plus assez de pions pour gagner (Katarenga uniquement)
            if current_game_mode == 0 and not game_over:
                forced_victory = check_minimum_pawn_victory_condition(pawn_grid, current_game_mode)
                if forced_victory > 0:
                    winner = forced_victory
                    game_over = True

            # Passer au joueur suivant si le jeu n’est pas terminé
            if not game_over:
                current_player = 3 - current_player

            animation.complete_animation()

        
        # Dessiner les mouvements possibles
        if (selected_pawn and possible_moves and not game_over and 
            not animation.is_moving() and current_game_mode in [0, 1]):
            highlight_possible_moves(screen, possible_moves, board_x, board_y, cell_size)
        
        # Mettre en surbrillance les pions connectés si le jeu est terminé en mode Congress
        if game_over and winner > 0 and current_game_mode == 1:
            player_color = DARK_RED if winner == 1 else DARK_BLUE
            highlight_connected_pawns(screen, connected_pawns, board_x, board_y, cell_size, player_color)

        # Afficher le message de victoire unifié pour tous les modes
        if game_over and winner > 0:
            display_victory_message(screen, winner)
        
        # Afficher le joueur actuel sauf si le jeu est terminé
        if not game_over:
            player_text = font.render(f"Tour du joueur: {'Rouge' if current_player == 1 else 'Bleu'}", True, DARK_RED if current_player == 1 else DARK_BLUE)
            screen.blit(player_text, (current_width - 200, 20))
        
        # Afficher des informations spécifiques au mode de jeu
        mode_names = ["Katarenga", "Congress", "Isolation"]
        mode_text = font.render(f"Mode: {mode_names[current_game_mode]}", True, BLACK)
        screen.blit(mode_text, (current_width - 200, 50))

        # Dessiner le bouton retour Abandonner
        text_width, text_height = font.size("Abandonner")
        back_button = pygame.Rect(back_button.x, back_button.y, text_width + 20, text_height + 10)
        pygame.draw.rect(screen, RED, back_button)
        back_text = font.render("Abandonner", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, back_text_rect)
        
        # Traitement de l'IA
        if (
            not game_over
            and current_player == 2
            and not animation.is_moving()
            and not animation.has_pending_move()
            and GLOBAL_SELECTED_OPPONENT == 0
            and current_game_mode in [0, 1]  # IA seulement pour Katarenga et Congress
        ):
            ai_move = randomAi(pawn_grid, board_grid, 2, current_game_mode)
            if ai_move:
                from_row, from_col, (to_row, to_col) = ai_move
                animation.start_move(from_row, from_col, to_row, to_col, board_x, board_y, cell_size, pawn_grid[from_row][from_col])
                animation.pending_move = {
                    'from': (from_row, from_col),
                    'to': (to_row, to_col),
                    'pawn_color': pawn_grid[from_row][from_col]
                }
                selected_pawn = None
                possible_moves = []
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Quitter bouton abandonner
                if back_button.collidepoint(event.pos):
                    display_victory_message(screen, 0)
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    return
                
                # clic sur le plateau (seulement si le jeu n'est pas terminé et aucune animation)
                if not game_over and not animation.is_moving():
                    mouse_x, mouse_y = event.pos
                    # Si le clic est dans les limites du plateau
                    if (board_x <= mouse_x < board_x + board_size and 
                        board_y <= mouse_y < board_y + board_size):

                        # Convertir les coordonnées du clic en indices de la grille
                        col = (mouse_x - board_x) // cell_size
                        row = (mouse_y - board_y) // cell_size
                        
                        # Mode Isolation avec la logique de placement de pions
                        if current_game_mode == 2:  # Mode Isolation
                            # Limiter aux cases de jeu 8x8
                            if 1 <= row <= 8 and 1 <= col <= 8:
                                if place_pawn(pawn_grid, row, col, current_player, board_grid):
                                    game_over, winner = check_isolation_victory(pawn_grid, current_player, board_grid)                            
                                    if not game_over:
                                        # Passer au joueur suivant
                                        current_player = 2 if current_player == 1 else 1
                        
                        elif current_game_mode in [0, 1]:  # Katarenga ou Congress
                            if game_phase == "play":
                                # Si un pion est déjà sélectionné
                                if selected_pawn:
                                    selected_row, selected_col = selected_pawn
                                    
                                    # Vérifier si le clic est sur l'un des mouvements possibles
                                    if (row, col) in possible_moves:
                                        # Gestion spéciale pour Katarenga et les camps
                                        if current_game_mode == 0:
                                            from katarenga import get_camp_positions, place_in_camp, check_katarenga_victory
                                            camp_positions = get_camp_positions(current_player)
                                            
                                            if (row, col) in camp_positions:
                                                # Placement direct dans un camp
                                                if place_in_camp(row, col, pawn_grid, current_player):
                                                    pawn_grid[selected_row][selected_col] = 0
                                                    winner = check_katarenga_victory()
                                                    game_over = winner > 0
                                                    if not game_over:
                                                        current_player = 3 - current_player
                                                    selected_pawn = None
                                                    possible_moves = []
                                                    continue
                                        
                                        # Démarrer l'animation normale
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
                                        possible_moves = get_valid_moves_with_mode(row, col, board_grid, pawn_grid, current_game_mode)
                                    
                                    # Si le clic est ailleurs, annuler la sélection
                                    else:
                                        selected_pawn = None
                                        possible_moves = []
                                
                                # Si aucun pion n'est sélectionné
                                else:
                                    # Pour Katarenga, permettre la sélection sur tout le plateau 10x10
                                    if current_game_mode == 0:
                                        if 0 <= row < 10 and 0 <= col < 10 and pawn_grid[row][col] == current_player:
                                            selected_pawn = (row, col)
                                            possible_moves = get_valid_moves_with_mode(row, col, board_grid, pawn_grid, current_game_mode)
                                    else:
                                        # Pour Congress et Isolation, limiter à la zone 8x8
                                        if 1 <= row <= 8 and 1 <= col <= 8 and pawn_grid[row][col] == current_player:
                                            selected_pawn = (row, col)
                                            possible_moves = get_valid_moves_with_mode(row, col, board_grid, pawn_grid, current_game_mode)
                
        pygame.display.flip()
        clock.tick(60)  # 60 FPS pour des animations fluides


def display_victory_message(screen, winner):
    """
    Affiche un message de victoire à l'écran.
    """
    
    message_color = (0, 150, 0) # Vert
    text_color = (255, 255, 255)  # Blanc
    
    # Police
    font = pygame.font.Font(None, 48)
    
    if winner == 0:
        message = "Partie abandonnée"
    else:
        message = f"Victoire du joueur {'Rouge' if winner == 1 else 'Bleu'} !"
    
    # Créer la surface du texte
    text = font.render(message, True, text_color)
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    
    # Créer un fond pour le message
    padding = 20
    message_rect = pygame.Rect(
        text_rect.left - padding,
        text_rect.top - padding,
        text_rect.width + 2 * padding,
        text_rect.height + 2 * padding
    )
    s = pygame.Surface((message_rect.width, message_rect.height), pygame.SRCALPHA)
    s.fill((message_color[0], message_color[1], message_color[2], 200)) 
    screen.blit(s, message_rect)
    
    # Dessiner une bordure
    pygame.draw.rect(screen, message_color, message_rect, 3)
    
    # Dessiner le texte
    screen.blit(text, text_rect)
    

def randomAi(pawn_grid, board_grid, current_player, game_mode):
    """
    IA simple qui choisit un mouvement aléatoire parmi les mouvements possibles.
    Version mise à jour qui utilise maintenant pawn.py pour tout.
    """
    from pawn import get_valid_moves
    possible_moves = []
    
    # Déterminer la taille de la grille selon le mode
    if game_mode == 0:  # Katarenga
        grid_range = range(10)
    else:  # Congress et Isolation
        grid_range = range(1, 9)
    
    # Trouver tous les pions du joueur actuel
    for row in grid_range:
        for col in grid_range:
            if pawn_grid[row][col] == current_player:
                moves = get_valid_moves(row, col, board_grid, pawn_grid, game_mode)
                possible_moves.extend([(row, col, move) for move in moves])
    
    # Si aucun mouvement possible, retourner None
    if not possible_moves:
        return None
    
    # Choisir un mouvement aléatoire
    chosen_move = random.choice(possible_moves)
    
    return chosen_move  # Retourne (from_row, from_col, (to_row, to_col))