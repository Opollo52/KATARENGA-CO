import pygame
from pawn import get_valid_moves

CELL_SIZE = 60
BOARD_SIZE = 8
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 100, 255)
RED = (255, 100, 100)

def draw_board(screen, board):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
            if board[row][col] == 1:
                pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 3)
            elif board[row][col] == 2:
                pygame.draw.circle(screen, BLUE, rect.center, CELL_SIZE // 3)

def is_position_safe(pawn_grid, row, col, board_grid):
    if pawn_grid[row][col] != 0:
        return False  # Case déjà occupée
    
    # Vérifier tous les pions existants sur le plateau
    for r in range(8):
        for c in range(8):
            if pawn_grid[r][c] != 0:  # Il y a un pion à cette position
                # Obtenir tous les mouvements possibles de ce pion
                possible_moves = get_valid_moves(r, c, board_grid, pawn_grid)
                
                # Si ce pion peut atteindre notre position, alors elle n'est pas sûre
                if (row, col) in possible_moves:
                    return False
    
    return True

def place_pawn(pawn_grid, row, col, player, board_grid):
    if pawn_grid[row][col] != 0:
        return False  # Case déjà occupée
    
    # Vérifier si la position est sûre (pas en prise)
    if not is_position_safe(pawn_grid, row, col, board_grid):
        return False
    
    # Placer le pion
    pawn_grid[row][col] = player
    return True

def get_all_safe_positions(pawn_grid, board_grid, player):
    safe_positions = []
    for r in range(8):
        for c in range(8):
            if is_position_safe(pawn_grid, r, c, board_grid):
                safe_positions.append((r, c))
    return safe_positions

def check_isolation_victory(pawn_grid, current_player, board_grid):
    next_player = 2 if current_player == 1 else 1
    safe_positions = get_all_safe_positions(pawn_grid, board_grid, next_player)
    
    if not safe_positions:
        # L'adversaire ne peut plus jouer, le joueur actuel gagne
        return True, current_player
    
    return False, 0

def highlight_safe_positions(screen, safe_positions, board_x, board_y, cell_size):
    for r, c in safe_positions:
        x = board_x + c * cell_size + cell_size // 2
        y = board_y + r * cell_size + cell_size // 2
        # Dessiner un cercle vert semi-transparent
        pygame.draw.circle(screen, (0, 255, 0), (x, y), cell_size // 6)

def run_isolation(screen):
    clock = pygame.time.Clock()
    board_grid = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    pawn_grid = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    current_player = 1
    running = True

    while running:
        screen.fill((200, 200, 200))
        draw_board(screen, pawn_grid)
        
        # Afficher une croix sur les cases non valides pour le joueur actuel
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if not is_position_safe(pawn_grid, r, c, board_grid):
                    draw_cross(screen, r, c, CELL_SIZE)
        
        # Afficher les positions sûres pour le joueur actuel
        safe_positions = get_all_safe_positions(pawn_grid, board_grid, current_player)
        highlight_safe_positions(screen, safe_positions, 0, 0, CELL_SIZE)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                row, col = mouse_y // CELL_SIZE, mouse_x // CELL_SIZE

                if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                    if place_pawn(pawn_grid, row, col, current_player, board_grid):
                        # Vérifier si l'autre joueur peut encore jouer
                        game_over, winner = check_isolation_victory(pawn_grid, current_player, board_grid)
                        
                        if game_over:
                            print(f"Le joueur {winner} ({'Rouge' if winner == 1 else 'Bleu'}) a gagné !")
                            running = False
                        else:
                            # Passer au joueur suivant
                            current_player = 2 if current_player == 1 else 1

        clock.tick(30)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((CELL_SIZE * BOARD_SIZE, CELL_SIZE * BOARD_SIZE))
    pygame.display.set_caption("Isolation")
    run_isolation(screen)
    pygame.quit()