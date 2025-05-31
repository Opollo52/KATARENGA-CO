from plateau.game_modes import GLOBAL_SELECTED_GAME
import pygame
class Pawn:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.selected = False

def get_valid_moves(row, col, board_grid, pawn_grid, game_mode=None):
    """
    Obtenir les mouvements valides d'un pion à une position donnée.
    Gestion unifiée pour tous les modes de jeu avec grille 10x10 harmonisée.
    """
    # Utiliser le mode global si non spécifié
    if game_mode is None:
        game_mode = GLOBAL_SELECTED_GAME
    
    # Isolation: aucun déplacement de pions, seulement placement
    if game_mode == 2:
        return []
    
    # Vérifier s'il y a un pion à cette position
    if pawn_grid[row][col] == 0:
        return []
    
    # Couleur du pion
    pawn_color = pawn_grid[row][col]
    
    # Obtenir la couleur de la case où se trouve le pion
    cell_color = board_grid[row][col]
    
    # Liste des mouvements possibles
    possible_moves = []
    
    # Déterminer les limites du plateau selon le mode
    if game_mode == 0:  # Katarenga - grille complète 10x10
        min_coord = 0
        max_coord = 10
        playable_min = 1
        playable_max = 8
    else:  # Congress - zone 8x8 dans grille 10x10
        min_coord = 1
        max_coord = 9
        playable_min = 1
        playable_max = 8
    
    # Pour Katarenga, vérifier si on peut aller aux camps
    camp_moves = []
    if game_mode == 0:
        from jeux.katarenga import is_on_enemy_baseline, get_camp_positions
        if is_on_enemy_baseline(row, pawn_color):
            camp_positions = get_camp_positions(pawn_color)
            for camp_row, camp_col in camp_positions:
                if pawn_grid[camp_row][camp_col] == 0:  # Camp vide
                    camp_moves.append((camp_row, camp_col))
    
    # Déplacement selon la couleur de la case
    if cell_color == 3:  # Bleu: déplacement en roi 
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for move_row, move_column in directions:
            r, c = row + move_row, col + move_column
            if min_coord <= r < max_coord and min_coord <= c < max_coord:
                # Zone de jeu normale
                if playable_min <= r <= playable_max and playable_min <= c <= playable_max:
                    # Si la case est vide, toujours autorisé
                    if pawn_grid[r][c] == 0:
                        possible_moves.append((r, c))
                    # Si la case contient un pion ennemi et que le mode est Katarenga
                    elif pawn_grid[r][c] != pawn_color and game_mode == 0:
                        possible_moves.append((r, c))
                    # Congress: pas de capture
                    elif game_mode == 1 and pawn_grid[r][c] == 0:
                        possible_moves.append((r, c))
    
    elif cell_color == 4:  # Rouge: déplacement en tour
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for move_row, move_column in directions:
            r, c = row + move_row, col + move_column
            # Continuer dans cette direction jusqu'à rencontrer un obstacle
            while min_coord <= r < max_coord and min_coord <= c < max_coord:
                # Zone de jeu normale
                if playable_min <= r <= playable_max and playable_min <= c <= playable_max:
                    # Si la case est vide
                    if pawn_grid[r][c] == 0:
                        possible_moves.append((r, c))
                    else:
                        # Si la case contient un pion ennemi et que le mode autorise la capture (Katarenga)
                        if pawn_grid[r][c] != pawn_color and game_mode == 0:
                            possible_moves.append((r, c))
                        break  # On ne peut pas aller plus loin
                    
                    # Si c'est aussi une case rouge, c'est la dernière case accessible
                    if board_grid[r][c] == 4:
                        break
                else:
                    break
                
                # Avancer d'une case dans la même direction
                r += move_row
                c += move_column
    
    elif cell_color == 1:  # Jaune: déplacement en fou
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for move_row, move_column in directions:
            r, c = row + move_row, col + move_column
            # Continuer dans cette direction jusqu'à rencontrer un obstacle
            while min_coord <= r < max_coord and min_coord <= c < max_coord:
                # Zone de jeu normale
                if playable_min <= r <= playable_max and playable_min <= c <= playable_max:
                    # Si la case est vide
                    if pawn_grid[r][c] == 0:
                        possible_moves.append((r, c))
                    else:
                        # Si la case contient un pion ennemi et que le mode est Katarenga
                        if pawn_grid[r][c] != pawn_color and game_mode == 0:
                            possible_moves.append((r, c))
                        break # On ne peut pas aller plus loin
                    
                    # Si c'est aussi une case jaune, c'est la dernière case accessible
                    if board_grid[r][c] == 1:  # Jaune
                        break
                else:
                    break
                
                # Avancer d'une case dans la même direction
                r += move_row
                c += move_column
    
    elif cell_color == 2:  # Vert: déplacement en cavalier
        knight_moves = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2),  (1, 2),
            (2, -1),  (2, 1)
        ]
        
        for move_row, move_column in knight_moves:
            r, c = row + move_row, col + move_column
            if min_coord <= r < max_coord and min_coord <= c < max_coord:
                # Zone de jeu normale
                if playable_min <= r <= playable_max and playable_min <= c <= playable_max:
                    # Si la case est vide
                    if pawn_grid[r][c] == 0:
                        possible_moves.append((r, c))
                    # Si la case contient un pion ennemi et que le mode est Katarenga
                    elif pawn_grid[r][c] != pawn_color and game_mode == 0:
                        possible_moves.append((r, c))
                    # Congress: pas de capture
                    elif game_mode == 1 and pawn_grid[r][c] == 0:
                        possible_moves.append((r, c))
    
    # Ajouter les mouvements vers les camps pour Katarenga
    if game_mode == 0:
        possible_moves.extend(camp_moves)
    
    return possible_moves

def highlight_possible_moves(screen, possible_moves, board_x, board_y, cell_size):
    """
    Met en surbrillance les mouvements possibles sur l'écran avec des petits points noirs
    """
    # Définir la taille du point
    dot_radius = cell_size // 8
    
    # Afficher un point noir pour chaque mouvement possible
    for r, c in possible_moves:
        x = board_x + c * cell_size + cell_size // 2
        y = board_y + r * cell_size + cell_size // 2
        pygame.draw.circle(screen, (0, 0, 0), (x, y), dot_radius)

def is_valid_move(from_row, from_col, to_row, to_col, board_grid, pawn_grid, game_mode=None):
    """
    Vérifie si un mouvement d'une position à une autre est valide
    """
    # Vérifier s'il y a un pion à la position de départ
    if pawn_grid[from_row][from_col] == 0:
        return False
    
    # Calculer les mouvements possibles
    possible_moves = get_valid_moves(from_row, from_col, board_grid, pawn_grid, game_mode)
    
    # Vérifier si la position d'arrivée est dans les mouvements possibles
    return (to_row, to_col) in possible_moves