import pygame

# Variables globales pour les camps (en dehors du plateau 8x8)
camps_player1 = {"camp1": [], "camp2": []}  # Camps du joueur 1 (rouge)
camps_player2 = {"camp1": [], "camp2": []}  # Camps du joueur 2 (bleu)

def reset_camps():
    global camps_player1, camps_player2
    camps_player1 = {"camp1": [], "camp2": []}
    camps_player2 = {"camp1": [], "camp2": []}

def is_on_enemy_baseline(row, player):
    """Vérifie si le pion est sur la ligne de base ennemie"""
    if player == 1:  # Joueur rouge
        return row == 8  # Ligne de base du joueur bleu
    else:  # Joueur bleu
        return row == 1  # Ligne de base du joueur rouge

def get_camp_positions(player):
    """Retourne les positions des camps pour un joueur"""
    if player == 1:  # Joueur rouge vise les camps rouges (en bas)
        return [(9, 0), (9, 9)]  # Camps rouges en bas
    else:  # Joueur bleu vise les camps bleus (en haut)
        return [(0, 0), (0, 9)]  # Camps bleus en haut

def is_camp_occupied(row, col, player):
    """Vérifie si un camp est déjà occupé AVANT de tenter le mouvement"""
    global camps_player1, camps_player2
    
    camp_positions = get_camp_positions(player)
    
    if (row, col) not in camp_positions:
        return False  # Ce n'est pas un camp
    
    if player == 1:  # Rouge vérifie ses camps rouges
        if (row, col) == (9, 0):
            return len(camps_player1["camp1"]) > 0
        else:  # (9, 9)
            return len(camps_player1["camp2"]) > 0
    else:  # Bleu vérifie ses camps bleus
        if (row, col) == (0, 0):
            return len(camps_player2["camp1"]) > 0
        else:  # (0, 9)
            return len(camps_player2["camp2"]) > 0

def place_in_camp(row, col, pawn_grid, player):
    """Place un pion dans un camp et le retire du jeu - LIMITE À UN PION PAR CAMP"""
    global camps_player1, camps_player2
    
    camp_positions = get_camp_positions(player)
    
    if (row, col) in camp_positions:
        # Vérifier si le camp est déjà occupé (limite d'un pion par camp)
        if player == 1:  # Rouge va dans ses camps rouges
            if (row, col) == (9, 0):
                if len(camps_player1["camp1"]) == 0:  # Camp vide
                    camps_player1["camp1"].append(player)  # Rouge entre dans son camp 1
                    return True
                else:
                    return False  # Camp déjà occupé
            else:  # (9, 9)
                if len(camps_player1["camp2"]) == 0:  # Camp vide
                    camps_player1["camp2"].append(player)  # Rouge entre dans son camp 2
                    return True
                else:
                    return False  # Camp déjà occupé
        else:  # Bleu va dans ses camps bleus
            if (row, col) == (0, 0):
                if len(camps_player2["camp1"]) == 0:  # Camp vide
                    camps_player2["camp1"].append(player)  # Bleu entre dans son camp 1
                    return True
                else:
                    return False  # Camp déjà occupé
            else:  # (0, 9)
                if len(camps_player2["camp2"]) == 0:  # Camp vide
                    camps_player2["camp2"].append(player)  # Bleu entre dans son camp 2
                    return True
                else:
                    return False  # Camp déjà occupé
    
    return False

def check_katarenga_victory():
    """Vérifie si un joueur a gagné en occupant ses 2 camps"""
    # Joueur 1 (rouge) gagne s'il occupe ses 2 camps rouges
    camps_occupied_by_player1 = 0
    if len(camps_player1["camp1"]) > 0:
        camps_occupied_by_player1 += 1
    if len(camps_player1["camp2"]) > 0:
        camps_occupied_by_player1 += 1
    
    if camps_occupied_by_player1 >= 2:
        return 1
    
    # Joueur 2 (bleu) gagne s'il occupe ses 2 camps bleus
    camps_occupied_by_player2 = 0
    if len(camps_player2["camp1"]) > 0:
        camps_occupied_by_player2 += 1
    if len(camps_player2["camp2"]) > 0:
        camps_occupied_by_player2 += 1
    
    if camps_occupied_by_player2 >= 2:
        return 2
    
    return 0

def draw_camps(screen, board_x, board_y, cell_size):
    # Couleurs
    RED = (200, 50, 50)
    BLUE = (50, 50, 200)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    
    # Positions des camps dans les coins absolus du frame
    camp_positions = [
        (0, 0), (0, 9),  # Camps bleus en haut
        (9, 0), (9, 9)   # Camps rouges en bas
    ]
    
    for row, col in camp_positions:
        # Calculer la position dans le coin du frame
        # Les camps sont dans le frame mais en dehors du plateau 8x8
        camp_rect = pygame.Rect(
            board_x + col * cell_size,
            board_y + row * cell_size,
            cell_size,
            cell_size
        )
        
        # Identifier le type de camp
        is_blue_camp = (row == 0)  # Camps du haut = bleus
        is_red_camp = (row == 9)   # Camps du bas = rouges
        
        # Dessiner seulement si le camp contient des pions
        has_pions = False
        pion_color = None
        
        if is_blue_camp:
            if col == 0 and len(camps_player2["camp1"]) > 0:
                has_pions = True
                pion_color = BLUE
            elif col == 9 and len(camps_player2["camp2"]) > 0:
                has_pions = True
                pion_color = BLUE
        elif is_red_camp:
            if col == 0 and len(camps_player1["camp1"]) > 0:
                has_pions = True
                pion_color = RED
            elif col == 9 and len(camps_player1["camp2"]) > 0:
                has_pions = True
                pion_color = RED
        
        # Dessiner le camp seulement s'il y a des pions
        if has_pions:
            # Dessiner un cercle pour représenter le pion dans le camp
            pygame.draw.circle(screen, pion_color, camp_rect.center, cell_size // 3)
            pygame.draw.circle(screen, BLACK, camp_rect.center, cell_size // 3, 3)
            
            # Plus besoin d'afficher le nombre car il n'y a qu'un pion maximum par camp

def has_pion_in_camp(player):
    if player == 1:  # Rouge
        return len(camps_player1["camp1"]) > 0 or len(camps_player1["camp2"]) > 0
    else:  # Bleu
        return len(camps_player2["camp1"]) > 0 or len(camps_player2["camp2"]) > 0

def check_minimum_pawn_victory_condition(pawn_grid, game_mode):
    if game_mode != 0:
        return 0  # Ne s'applique qu'à Katarenga
    
    red_pawns = sum(row.count(1) for row in pawn_grid)
    blue_pawns = sum(row.count(2) for row in pawn_grid)
    
    # Vérifier si les joueurs ont des pions dans leurs camps
    red_has_camp_pion = has_pion_in_camp(1)
    blue_has_camp_pion = has_pion_in_camp(2)
    
    # Règles modifiées pour la victoire par élimination
    if red_pawns == 1 and not red_has_camp_pion:
        return 2  # Bleu gagne : Rouge n'a qu'1 pion et aucun pion dans un camp
    elif blue_pawns == 1 and not blue_has_camp_pion:
        return 1  # Rouge gagne : Bleu n'a qu'1 pion et aucun pion dans un camp
    elif red_pawns == 0:
        return 2  # Bleu gagne : Rouge n'a plus de pions
    elif blue_pawns == 0:
        return 1  # Rouge gagne : Bleu n'a plus de pions
    
    return 0  # Aucun gagnant encore