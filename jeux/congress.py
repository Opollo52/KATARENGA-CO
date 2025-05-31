import pygame

def connected(row, col, pawn_grid, player, visited, directions):
    """
    Fonction récursive pour explorer les pions connectés.
    """
    # Si la position est déjà visitée ou n'appartient pas au joueur, on arrête
    if (row, col) in visited or pawn_grid[row][col] != player:
        return

    # Marquer la position comme visitée
    visited.append((row, col))
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc

        # Vérifier si dans les limites de la grille
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            connected(new_row, new_col, pawn_grid, player, visited, directions)


def find_connected_pawns(pawn_grid, start_pos, player):
    """
    Trouve tous les pions connectés à partir d'une position de départ.
    """
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Haut, Bas, Gauche, Droite

    visited = []  # Liste pour stocker les positions visitées
    
    connected(start_pos[0], start_pos[1], pawn_grid, player, visited, directions)

    return visited 

def check_victory(pawn_grid):
    """
    Vérifie si l'une des conditions de victoire du mode Congress est remplie.
    """
    # Vérifier la victoire pour chaque joueur
    for player in [1, 2]:
        player_pawns = []
        for row in range(8):
            for col in range(8):
                if pawn_grid[row][col] == player:
                    player_pawns.append((row, col))
        # Vérifier si tous les pions forment un bloc connecté
        connected_pawns = find_connected_pawns(pawn_grid, player_pawns[0], player)
        
        # Si tous les pions du joueur sont connectés, c'est une victoire
        if len(connected_pawns) == len(player_pawns):
            return player, connected_pawns
    
    # Aucune victoire
    return 0, []

def highlight_connected_pawns(screen, connected_pawns, board_x, board_y, cell_size, player_color):
    """
    Met en surbrillance les pions connectés sur l'écran pour montrer la victoire.
    """
    highlight_color = (255, 255, 0) # Jaune
    highlight_thickness = 3
    
    # Dessiner un cercle de surbrillance autour de chaque pion connecté
    for row, col in connected_pawns:
        x = board_x + col * cell_size + cell_size // 2
        y = board_y + row * cell_size + cell_size // 2
        
        radius = cell_size // 3 + 5
        
        pygame.draw.circle(screen, highlight_color, (x, y), radius, highlight_thickness)

def display_victory_message(screen, winner):
    """
    Affiche un message de victoire à l'écran.
    """
    
    message_color = (0, 150, 0) # Vert
    text_color = (255, 255, 255)  # Blanc
    
    # Police
    font = pygame.font.Font(None, 48)
    
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
