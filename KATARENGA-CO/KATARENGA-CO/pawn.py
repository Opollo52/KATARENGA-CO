import numpy as np
from game_modes import GLOBAL_SELECTED_GAME, GLOBAL_SELECTED_OPPONENT
import pygame

class Pawn:
    def __init__(self, row, col, color):
        """
        Initialise un pion
        """
        self.row = row
        self.col = col
        self.color = color
        self.selected = False
    
def get_valid_moves(row, col, board_grid, pawn_grid):
    """
    obtenir les mouvements valides d'un pion à une position donnée.
    """
    # Importation dynamique pour s'assurer que la variable est à jour
    from game_modes import GLOBAL_SELECTED_GAME
    
    # Si mode 2 (Isolation), aucun déplacement n'est autorisé (pendant la phase de jeu)
    if GLOBAL_SELECTED_GAME == 2:
        return []
    
    # Vérifier s'il y a un pion à cette position
    if pawn_grid[row][col] == 0:
        return []
    
    # Couleur du pion (1 = rouge, 2 = bleu)
    pawn_color = pawn_grid[row][col]
    
    # Obtenir la couleur de la case où se trouve le pion
    cell_color = board_grid[row][col]
    
    # Liste des mouvements possibles
    possible_moves = []
    
    # Déplacement selon la couleur de la case
    if cell_color == 3:  # Bleu: déplacement en roi (une case dans toutes les directions)
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                # Si la case est vide, toujours autorisé
                if pawn_grid[r][c] == 0:
                    possible_moves.append((r, c))
                # Si la case contient un pion ennemi et que le mode autorise la capture (Katarenga)
                elif pawn_grid[r][c] != pawn_color and GLOBAL_SELECTED_GAME == 0:
                    possible_moves.append((r, c))
    
    elif cell_color == 4:  # Rouge: déplacement en tour (horizontalement et verticalement)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Haut, bas, gauche, droite
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            # Continuer dans cette direction jusqu'à rencontrer un obstacle
            while 0 <= r < 8 and 0 <= c < 8:
                # Si la case est vide
                if pawn_grid[r][c] == 0:
                    possible_moves.append((r, c))
                else:
                    # Si la case contient un pion ennemi et que le mode autorise la capture (Katarenga)
                    if pawn_grid[r][c] != pawn_color and GLOBAL_SELECTED_GAME == 0:
                        possible_moves.append((r, c))
                    break  # On ne peut pas aller plus loin
                
                # Si c'est aussi une case rouge, c'est la dernière case accessible
                if board_grid[r][c] == 4:  # Rouge
                    break
                
                # Avancer d'une case dans la même direction
                r += dr
                c += dc
    
    elif cell_color == 1:  # Jaune: déplacement en fou (diagonalement)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonales
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            # Continuer dans cette direction jusqu'à rencontrer un obstacle
            while 0 <= r < 8 and 0 <= c < 8:
                # Si la case est vide
                if pawn_grid[r][c] == 0:
                    possible_moves.append((r, c))
                else:
                    # Si la case contient un pion ennemi et que le mode autorise la capture (Katarenga)
                    if pawn_grid[r][c] != pawn_color and GLOBAL_SELECTED_GAME == 0:
                        possible_moves.append((r, c))
                    break  # On ne peut pas aller plus loin
                
                # Si c'est aussi une case jaune, c'est la dernière case accessible
                if board_grid[r][c] == 1:  # Jaune
                    break
                
                # Avancer d'une case dans la même direction
                r += dr
                c += dc
    
    elif cell_color == 2:  # Vert: déplacement en cavalier (en L)
        knight_moves = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2),  (1, 2),
            (2, -1),  (2, 1)
        ]
        
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                # Si la case est vide
                if pawn_grid[r][c] == 0:
                    possible_moves.append((r, c))
                # Si la case contient un pion ennemi et que le mode autorise la capture (Katarenga)
                elif pawn_grid[r][c] != pawn_color and GLOBAL_SELECTED_GAME == 0:
                    possible_moves.append((r, c))
    
    return possible_moves

def highlight_possible_moves(screen, possible_moves, board_x, board_y, cell_size):
    """
    Met en surbrillance les mouvements possibles sur l'écran avec des petits points noirs
    screen: surface Pygame
    possible_moves: liste de tuples (row, col)
    board_x, board_y: position du coin supérieur gauche du plateau sur l'écran
    cell_size: taille d'une cellule en pixels
    """
    import pygame  # Import local pour éviter la dépendance circulaire
    
    # Définir la taille du point
    dot_radius = cell_size // 8
    
    # Afficher un point noir pour chaque mouvement possible
    for r, c in possible_moves:
        x = board_x + c * cell_size + cell_size // 2
        y = board_y + r * cell_size + cell_size // 2
        pygame.draw.circle(screen, (0, 0, 0), (x, y), dot_radius)

# Fonction de test pour vérifier si un mouvement est valide
def is_valid_move(from_row, from_col, to_row, to_col, board_grid, pawn_grid):
    """
    Vérifie si un mouvement d'une position à une autre est valide
    """
    # Importation dynamique pour s'assurer que la variable est à jour
    from game_modes import GLOBAL_SELECTED_GAME
    
    # Vérifier s'il y a un pion à la position de départ
    if pawn_grid[from_row][from_col] == 0:
        return False
    
    # Calculer les mouvements possibles
    possible_moves = get_valid_moves(from_row, from_col, board_grid, pawn_grid)
    
    # Vérifier si la position d'arrivée est dans les mouvements possibles
    return (to_row, to_col) in possible_moves