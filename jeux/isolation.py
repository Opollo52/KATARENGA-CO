import pygame
from save.save_game import save_manager
from plateau.pawn import get_valid_moves

def is_position_safe_isolation(pawn_grid, row, col, board_grid):
    """
    Vérifie si une position est sûre pour le placement d'un pion en mode Isolation.
    Une position est sûre si aucun pion existant ne peut l'atteindre.
    Utilise la grille 10x10 harmonisée avec la zone de jeu 8x8 (indices 1-8).
    """
    if pawn_grid[row][col] != 0:
        return False  # Case déjà occupée
    
    # Vérifier tous les pions existants sur le plateau dans la zone de jeu 8x8
    for r in range(1, 9):
        for c in range(1, 9):
            if pawn_grid[r][c] != 0:  # Il y a un pion à cette position
                # Obtenir tous les mouvements possibles de ce pion
                # Pour Isolation, on utilise le mode de jeu 2
                possible_moves = get_valid_moves(r, c, board_grid, pawn_grid, game_mode=2)
                
                # Si ce pion peut atteindre notre position, alors elle n'est pas sûre
                if (row, col) in possible_moves:
                    return False
    
    return True

def place_pawn_isolation(pawn_grid, row, col, player, board_grid):
    """
    Place un pion en mode Isolation si la position est valide et sûre.
    Utilise la grille 10x10 harmonisée avec la zone de jeu 8x8.
    """
    # Vérifier que nous sommes dans la zone de jeu 8x8
    if not (1 <= row <= 8 and 1 <= col <= 8):
        return False
        
    if pawn_grid[row][col] != 0:
        return False  # Case déjà occupée
    
    # Vérifier si la position est sûre (pas en prise)
    if not is_position_safe_isolation(pawn_grid, row, col, board_grid):
        return False
    
    # Placer le pion
    pawn_grid[row][col] = player
    return True

def get_all_safe_positions_isolation(pawn_grid, board_grid, player):
    """
    Retourne toutes les positions sûres pour un joueur en mode Isolation.
    Utilise la grille 10x10 harmonisée avec la zone de jeu 8x8.
    """
    safe_positions = []
    for r in range(1, 9):  # Zone de jeu 8x8
        for c in range(1, 9):
            if is_position_safe_isolation(pawn_grid, r, c, board_grid):
                safe_positions.append((r, c))
    return safe_positions

def check_isolation_victory(pawn_grid, current_player, board_grid):
    """
    Vérifie les conditions de victoire pour le mode Isolation.
    Le joueur qui vient de jouer gagne si l'adversaire ne peut plus jouer.
    Utilise la grille 10x10 harmonisée.
    """
    next_player = 2 if current_player == 1 else 1
    safe_positions = get_all_safe_positions_isolation(pawn_grid, board_grid, next_player)
    
    if not safe_positions:
        # L'adversaire ne peut plus jouer, le joueur actuel gagne
        return True, current_player
    
    return False, 0

# Fonctions de compatibilité pour l'ancien code (si nécessaire)
def place_pawn(pawn_grid, row, col, player, board_grid):
    """Fonction de compatibilité - redirige vers place_pawn_isolation"""
    return place_pawn_isolation(pawn_grid, row, col, player, board_grid)

def is_position_safe(pawn_grid, row, col, board_grid):
    """Fonction de compatibilité - redirige vers is_position_safe_isolation"""
    return is_position_safe_isolation(pawn_grid, row, col, board_grid)

def get_all_safe_positions(pawn_grid, board_grid, player):
    """Fonction de compatibilité - redirige vers get_all_safe_positions_isolation"""
    return get_all_safe_positions_isolation(pawn_grid, board_grid, player)

def highlight_safe_positions(screen, safe_positions, board_x, board_y, cell_size):
    """
    Met en surbrillance les positions sûres (pas utilisé dans game_board.py mais conservé)
    """
    for r, c in safe_positions:
        x = board_x + c * cell_size + cell_size // 2
        y = board_y + r * cell_size + cell_size // 2
        # Dessiner un cercle vert semi-transparent
        pygame.draw.circle(screen, (0, 255, 0), (x, y), cell_size // 6)

def draw_cross(screen, row, col, cell_size):
    """
    Dessine une croix rouge sur une case pour indiquer qu'elle n'est pas valide
    (pas utilisé dans game_board.py mais conservé pour compatibilité)
    """
    x = col * cell_size
    y = row * cell_size
    
    # Marges pour que la croix ne touche pas les bords de la case
    margin = cell_size // 4
    
    # Dessiner les deux lignes de la croix en rouge
    pygame.draw.line(screen, (255, 0, 0), 
                     (x + margin, y + margin), 
                     (x + cell_size - margin, y + cell_size - margin), 3)
    pygame.draw.line(screen, (255, 0, 0), 
                     (x + cell_size - margin, y + margin), 
                     (x + margin, y + cell_size - margin), 3)

def draw_board(screen, board):
    """
    Fonction de compatibilité pour dessiner le plateau (ancienne version)
    """
    CELL_SIZE = 60
    BOARD_SIZE = 8
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE = (100, 100, 255)
    RED = (255, 100, 100)
    
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
            if board[row][col] == 1:
                pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 3)
            elif board[row][col] == 2:
                pygame.draw.circle(screen, BLUE, rect.center, CELL_SIZE // 3)

def run_isolation(screen):
    """
    Version autonome du jeu Isolation (pour compatibilité avec main.py)
    Utilise maintenant la grille 10x10 harmonisée
    """
    clock = pygame.time.Clock()
    
    # Créer un plateau de base avec des cases colorées pour tester
    board_grid = [[0 for _ in range(10)] for _ in range(10)]
    # Remplir la zone de jeu avec des couleurs de base
    for row in range(1, 9):
        for col in range(1, 9):
            board_grid[row][col] = ((row + col) % 4) + 1  # Alternance de couleurs 1-4
    
    pawn_grid = [[0 for _ in range(10)] for _ in range(10)]  # Grille 10x10 pour les pions
    current_player = 1
    running = True
    
    # Taille des cellules pour affichage
    CELL_SIZE = min(screen.get_width(), screen.get_height()) // 12
    board_size = 10 * CELL_SIZE
    board_x = (screen.get_width() - board_size) // 2
    board_y = (screen.get_height() - board_size) // 2

    while running:
        screen.fill((200, 200, 200))
        
        # Dessiner le plateau (zone 8x8)
        for row in range(1, 9):
            for col in range(1, 9):
                rect = pygame.Rect(
                    board_x + col * CELL_SIZE, 
                    board_y + row * CELL_SIZE, 
                    CELL_SIZE, 
                    CELL_SIZE
                )
                
                # Couleur de fond selon la valeur du plateau
                colors = {
                    1: (255, 255, 0),  # Jaune
                    2: (0, 255, 0),    # Vert
                    3: (0, 0, 255),    # Bleu
                    4: (255, 0, 0)     # Rouge
                }
                
                cell_value = board_grid[row][col]
                if cell_value in colors:
                    pygame.draw.rect(screen, colors[cell_value], rect)
                else:
                    pygame.draw.rect(screen, (255, 255, 255), rect)
                
                pygame.draw.rect(screen, (0, 0, 0), rect, 2)
                
                # Dessiner les pions
                if pawn_grid[row][col] == 1:
                    pygame.draw.circle(screen, (200, 50, 50), rect.center, CELL_SIZE // 3)
                elif pawn_grid[row][col] == 2:
                    pygame.draw.circle(screen, (50, 50, 200), rect.center, CELL_SIZE // 3)
                
                # Dessiner une croix sur les cases non valides
                if pawn_grid[row][col] == 0 and not is_position_safe_isolation(pawn_grid, row, col, board_grid):
                    margin = CELL_SIZE // 4
                    pygame.draw.line(screen, (0, 0, 0), 
                                   (rect.left + margin, rect.top + margin), 
                                   (rect.right - margin, rect.bottom - margin), 4)
                    pygame.draw.line(screen, (0, 0, 0), 
                                   (rect.right - margin, rect.top + margin), 
                                   (rect.left + margin, rect.bottom - margin), 4)
        
        # Afficher le joueur actuel
        font = pygame.font.Font(None, 36)
        player_text = font.render(f"Joueur {'Rouge' if current_player == 1 else 'Bleu'}", True, (0, 0, 0))
        screen.blit(player_text, (20, 20))
        
    
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if save_button.collidepoint(event.pos):
                game_state = save_manager.create_game_state(
                    pawn_grid=pawn_grid,
                    board_grid=board_grid,
                    current_player=current_turn,
                    game_mode=current_game_mode
                )
                save_manager.save_game(game_state)
    
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Convertir en coordonnées de grille
                if (board_x <= mouse_x < board_x + board_size and 
                    board_y <= mouse_y < board_y + board_size):
                    
                    col = (mouse_x - board_x) // CELL_SIZE
                    row = (mouse_y - board_y) // CELL_SIZE

                    # Vérifier que c'est dans la zone de jeu 8x8
                    if 1 <= row <= 8 and 1 <= col <= 8:
                        if place_pawn_isolation(pawn_grid, row, col, current_player, board_grid):
                            # Vérifier si l'autre joueur peut encore jouer
                            game_over, winner = check_isolation_victory(pawn_grid, current_player, board_grid)
                            
                            if game_over:
                                print(f"Le joueur {winner} ({'Rouge' if winner == 1 else 'Bleu'}) a gagné !")
                                pygame.time.delay(2000)
                                running = False
                            else:
                                # Passer au joueur suivant
                                current_player = 2 if current_player == 1 else 1

        clock.tick(30)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Isolation")
    run_isolation(screen)
    pygame.quit()