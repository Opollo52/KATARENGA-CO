import pygame
import sys
import time
from pathlib import Path
from assets.colors import Colors
from plateau.game_board import create_game_board, initialize_pawns_for_game_mode, Animation
from plateau.pawn import get_valid_moves, highlight_possible_moves

def start_network_game(screen, network_manager):
    """
    Lance le jeu en réseau - VERSION CORRIGÉE POUR KATARENGA
    """
    print("=== DÉBUT NOUVELLE PARTIE RÉSEAU ===")
    
    pygame.display.set_caption("Partie en réseau")
    
    # Couleurs et ressources
    script_dir = Path(sys.argv[0]).parent.absolute()
    background_image = pygame.image.load(str(script_dir / "assets" / "img" / "fond.png"))
    
    WHITE = Colors.WHITE
    BLACK = Colors.BLACK
    BLUE = Colors.BLUE
    RED = Colors.RED
    GREEN = Colors.GREEN
    DARK_BLUE = Colors.DARK_BLUE 
    DARK_RED = Colors.DARK_RED
    
    # Images
    PATH = Path(sys.argv[0]).parent.absolute()
    images = {}
    images[1] = pygame.image.load(str(PATH / "assets" / "img" / "yellow.png"))  
    images[2] = pygame.image.load(str(PATH / "assets" / "img" / "green.png"))  
    images[3] = pygame.image.load(str(PATH / "assets" / "img" / "blue.png"))   
    images[4] = pygame.image.load(str(PATH / "assets" / "img" / "red.png"))
    frame_image = pygame.image.load(str(PATH / "assets" / "img" / "frame.png"))
    
    # SYNCHRONISATION MODE DE JEU
    import plateau.game_modes
    local_game_mode = plateau.game_modes.GLOBAL_SELECTED_GAME
    
    if network_manager.is_server:
        network_manager.send_message("game_mode", {"mode": local_game_mode})
        current_game_mode = local_game_mode
        my_player = 1
        opponent_player = 2
        
        # Attendre confirmation client
        timeout = time.time() + 10
        while time.time() < timeout:
            messages = network_manager.get_messages()
            for msg in messages:
                if msg['type'] == 'game_mode_confirm':
                    break
            else:
                pygame.time.wait(100)
                continue
            break
    else:
        # Recevoir mode du serveur
        timeout = time.time() + 10
        while time.time() < timeout:
            messages = network_manager.get_messages()
            for msg in messages:
                if msg['type'] == 'game_mode':
                    current_game_mode = msg['data']['mode']
                    network_manager.send_message("game_mode_confirm", {"mode": current_game_mode})
                    break
            else:
                pygame.time.wait(100)
                continue
            break
        
        my_player = 2
        opponent_player = 1
    
    print(f"Mode: {current_game_mode}, Mon joueur: {my_player}")
    
    # CONFIGURATION QUADRANTS
    from réseaux.network_quadrant_setup import show_network_quadrant_setup
    quadrants_data = show_network_quadrant_setup(screen, network_manager, network_manager.is_server)
    
    if quadrants_data is None:
        return
    
    # CRÉATION PLATEAU ET PIONS
    board_grid = create_game_board(quadrants_data)
    pawn_grid = initialize_pawns_for_game_mode(current_game_mode)
    animation = Animation()
    
    # INITIALISATION KATARENGA - CORRECTION CRITIQUE
    if current_game_mode == 0:
        from jeux.katarenga import reset_camps
        reset_camps()
        print("🎮 Camps Katarenga initialisés")
    
    # VARIABLES DE JEU - VERSION CORRIGÉE
    selected_pawn = None
    possible_moves = []
    current_player = 1
    game_over = False
    winner = 0
    connected_pawns = []
    victory_shown = False
    victory_message_sent = False
    game_ended = False
    
    font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    
    # FONCTION POUR TRAITER LES MESSAGES - CORRIGÉE POUR KATARENGA
    def process_messages():
        nonlocal pawn_grid, current_player, game_over, winner, connected_pawns
        nonlocal selected_pawn, possible_moves, victory_shown, victory_message_sent, game_ended
        
        messages = network_manager.get_messages()
        for msg in messages:
            if msg['type'] == 'move':
                from_pos = msg['data']['from']
                to_pos = msg['data']['to']
                
                print(f"📥 Mouvement reçu: {from_pos} -> {to_pos}")
                
                # Katarenga - camps spéciaux
                if current_game_mode == 0:
                    from jeux.katarenga import get_camp_positions, place_in_camp, check_katarenga_victory, is_camp_occupied
                    camp_positions = get_camp_positions(opponent_player)
                    
                    if to_pos in camp_positions:
                        if not is_camp_occupied(to_pos[0], to_pos[1], opponent_player) and place_in_camp(to_pos[0], to_pos[1], pawn_grid, opponent_player):
                            pawn_grid[from_pos[0]][from_pos[1]] = 0
                            winner = check_katarenga_victory()
                            if winner > 0:
                                game_over = True
                                game_ended = True
                                victory_shown = False
                                print(f"🏆 Victoire Katarenga reçue: Joueur {winner}")
                            else:
                                current_player = my_player  # Changement de tour seulement après placement camp
                            selected_pawn = None
                            possible_moves = []
                            return
                
                # MOUVEMENT NORMAL
                if current_game_mode == 1:  # Congress
                    pawn_grid[to_pos[0]][to_pos[1]] = pawn_grid[from_pos[0]][from_pos[1]]
                    pawn_grid[from_pos[0]][from_pos[1]] = 0
                    
                    from jeux.congress import check_victory
                    temp_grid = [[0 for _ in range(8)] for _ in range(8)]
                    for row in range(1, 9):
                        for col in range(1, 9):
                            temp_grid[row-1][col-1] = pawn_grid[row][col]
                    
                    winner, connected_pawns_temp = check_victory(temp_grid)
                    if winner > 0:
                        connected_pawns = [(row+1, col+1) for row, col in connected_pawns_temp]
                        game_over = True
                        game_ended = True
                        victory_shown = False
                        print(f"🏆 Victoire Congress: Joueur {winner}")
                    else:
                        current_player = my_player
                    
                    selected_pawn = None
                    possible_moves = []
                else:
                    # Animation pour Katarenga et Isolation
                    animation.start_move(
                        from_pos[0], from_pos[1], to_pos[0], to_pos[1],
                        board_x, board_y, cell_size,
                        pawn_grid[from_pos[0]][from_pos[1]]
                    )
                    
                    animation.pending_move = {
                        'from': from_pos,
                        'to': to_pos,
                        'pawn_color': pawn_grid[from_pos[0]][from_pos[1]]
                    }
                    
                    # AJOUT CRITIQUE: Forcer le changement de tour après animation
                    current_player = opponent_player
                    print(f"🎮 Tour forcé après animation: {current_player}")
            
            elif msg['type'] == 'placement':  # Isolation
                row, col = msg['data']['position']
                player = msg['data']['player']
                pawn_grid[row][col] = player
                
                from jeux.isolation import check_isolation_victory
                game_over_temp, winner_temp = check_isolation_victory(pawn_grid, player, board_grid)
                
                if game_over_temp:
                    game_over = True
                    game_ended = True
                    winner = winner_temp
                    victory_shown = False
                    print(f"🏆 Victoire Isolation: Joueur {winner}")
                else:
                    current_player = my_player
            
            elif msg['type'] == 'victory':
                winner = msg['data']['winner']
                game_over = True
                game_ended = True
                victory_shown = False
                print(f"🏆 Message de victoire reçu: Joueur {winner}")
                network_manager.send_message("victory_received", {"winner": winner})
            
            elif msg['type'] == 'victory_received':
                print(f"✅ Adversaire a reçu le message de victoire")
            
            elif msg['type'] == 'disconnect':
                print("🔌 Adversaire déconnecté")
                if not game_ended:
                    game_over = True
                    game_ended = True
                    victory_shown = False
    
    def send_move(from_pos, to_pos):
        network_manager.send_message("move", {
            "from": from_pos,
            "to": to_pos,
            "player": my_player,
            "change_turn": True  # Nouveau champ pour indiquer le changement de tour
        })
        # Changement de tour immédiat seulement pour le joueur local
        global current_player
        current_player = opponent_player
        print(f"Tour changé localement à {current_player}")
    
    def send_placement(position):
        network_manager.send_message("placement", {
            "position": position,
            "player": my_player
        })
    
    # SYNCHRONISATION FINALE
    if network_manager.is_server:
        network_manager.send_message("game_start", {"ready": True})
        timeout = time.time() + 5
        while time.time() < timeout:
            messages = network_manager.get_messages()
            for msg in messages:
                if msg['type'] == 'game_start_confirm':
                    break
            else:
                pygame.time.wait(100)
                continue
            break
    else:
        timeout = time.time() + 5
        while time.time() < timeout:
            messages = network_manager.get_messages()
            for msg in messages:
                if msg['type'] == 'game_start':
                    network_manager.send_message("game_start_confirm", {"ready": True})
                    break
            else:
                pygame.time.wait(100)
                continue
            break
    
    print("🚀 PARTIE DÉMARRÉE")
    
    # BOUCLE PRINCIPALE
    running = True
    while running:
        if not game_over:
            process_messages()
        
        # DIMENSIONS
        current_width, current_height = screen.get_size()
        
        if current_game_mode == 0:
            cell_size = min(current_width, current_height) // 12
            board_size = 10 * cell_size
        else:
            cell_size = min(current_width, current_height) // 10
            board_size = 8 * cell_size
        
        board_x = (current_width - board_size) // 2
        board_y = (current_height - board_size) // 2
        
        # Redimensionner images
        for key in images:
            images[key] = pygame.transform.scale(images[key], (cell_size, cell_size))
        
        # AFFICHAGE
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))
        
        # Cadre
        if frame_image:
            scaled_frame = pygame.transform.scale(frame_image, (
                board_size + 2 * cell_size,
                board_size + 2 * cell_size
            ))
            screen.blit(scaled_frame, (board_x - cell_size, board_y - cell_size))
        
        # PLATEAU
        if current_game_mode == 0:
            for row in range(10):
                for col in range(10):
                    if 1 <= row <= 8 and 1 <= col <= 8:
                        cell_value = board_grid[row][col]
                        cell_rect = pygame.Rect(
                            board_x + col * cell_size,
                            board_y + row * cell_size,
                            cell_size, cell_size
                        )
                        if cell_value in images:
                            screen.blit(images[cell_value], cell_rect)
                            pygame.draw.rect(screen, BLACK, cell_rect, 2)
            
            from jeux.katarenga import draw_camps
            draw_camps(screen, board_x, board_y, cell_size)
            
        else:
            for row in range(1, 9):
                for col in range(1, 9):
                    cell_value = board_grid[row][col]
                    cell_rect = pygame.Rect(
                        board_x + (col - 1) * cell_size,
                        board_y + (row - 1) * cell_size,
                        cell_size, cell_size
                    )
                    if cell_value in images:
                        screen.blit(images[cell_value], cell_rect)
                    pygame.draw.rect(screen, BLACK, cell_rect, 2)
        
        # PIONS
        draw_simple_pawns(screen, pawn_grid, board_x, board_y, cell_size, selected_pawn, animation, current_game_mode)
        
        # CROIX ISOLATION
        if current_game_mode == 2 and not game_over:
            draw_isolation_crosses(screen, pawn_grid, board_grid, board_x, board_y, cell_size)
        
        # ANIMATION - GESTION CORRIGÉE POUR KATARENGA
        if not animation.is_moving() and animation.has_pending_move() and not game_ended:
            from_pos = animation.pending_move['from']
            to_pos = animation.pending_move['to']
            
            pawn_grid[to_pos[0]][to_pos[1]] = pawn_grid[from_pos[0]][from_pos[1]]
            pawn_grid[from_pos[0]][from_pos[1]] = 0
            
            if current_game_mode == 0:
                from jeux.katarenga import check_minimum_pawn_victory_condition
                potential_winner = check_minimum_pawn_victory_condition(pawn_grid, current_game_mode)
                if potential_winner > 0 and not victory_message_sent:
                    winner = potential_winner
                    game_over = True
                    game_ended = True
                    victory_shown = False
                    victory_message_sent = True
                    print(f"🏆 Victoire Katarenga par élimination: Joueur {winner}")
                    network_manager.send_message("victory", {"winner": winner})
                # Ne pas changer le tour ici - déjà géré par l'expéditeur
            elif current_game_mode == 2:
                from jeux.isolation import check_isolation_victory
                game_over_temp, winner_temp = check_isolation_victory(pawn_grid, current_player, board_grid)
                if game_over_temp and not victory_message_sent:
                    winner = winner_temp
                    game_over = True
                    game_ended = True
                    victory_shown = False
                    victory_message_sent = True
                    print(f"🏆 Victoire Isolation: Joueur {winner}")
                    network_manager.send_message("victory", {"winner": winner})
                else:
                    current_player = my_player
            
            animation.moving_pawn = None
            animation.pending_move = None
        
        # VÉRIFICATION KATARENGA - CORRIGÉE
        if current_game_mode == 0 and not game_over and not game_ended:
            from jeux.katarenga import check_katarenga_victory, check_minimum_pawn_victory_condition
            
            potential_winner = check_katarenga_victory()
            if potential_winner > 0 and not victory_message_sent:
                winner = potential_winner
                game_over = True
                game_ended = True
                victory_shown = False
                victory_message_sent = True
                print(f"🏆 Victoire Katarenga par camps: Joueur {winner}")
                network_manager.send_message("victory", {"winner": winner})
                
                confirmation_timeout = time.time() + 2.0
                while time.time() < confirmation_timeout:
                    temp_messages = network_manager.get_messages()
                    for temp_msg in temp_messages:
                        if temp_msg['type'] == 'victory_received':
                            print("✅ Confirmation de victoire reçue")
                            break
                    else:
                        pygame.time.wait(50)
                        continue
                    break
            
            elif not victory_message_sent:
                elimination_winner = check_minimum_pawn_victory_condition(pawn_grid, current_game_mode)
                if elimination_winner > 0:
                    winner = elimination_winner
                    game_over = True
                    game_ended = True
                    victory_shown = False
                    victory_message_sent = True
                    print(f"🏆 Victoire Katarenga par élimination: Joueur {winner}")
                    network_manager.send_message("victory", {"winner": winner})
        
        # [RESTE DU CODE INCHANGÉ...]
        # ... (le reste de la fonction reste identique à la version originale)

# [LES FONCTIONS draw_simple_pawns, draw_simple_moves ET draw_isolation_crosses RESTENT IDENTIQUES]
            
            # Vérifier victoire par élimination (minimum de pions) seulement si pas de victoire par camps
            elif not victory_message_sent:
                elimination_winner = check_minimum_pawn_victory_condition(pawn_grid, current_game_mode)
                if elimination_winner > 0:
                    winner = elimination_winner
                    game_over = True
                    game_ended = True
                    victory_shown = False
                    victory_message_sent = True
                    print(f"🏆 Victoire Katarenga par élimination: Joueur {winner}")
                    network_manager.send_message("victory", {"winner": winner})
        
        # VÉRIFICATION ISOLATION
        if (current_game_mode == 2 and not game_over and current_player == my_player):
            # Test rapide si on peut encore jouer
            can_play = False
            for test_row in range(1, 9):
                for test_col in range(1, 9):
                    if pawn_grid[test_row][test_col] == 0:
                        # Test d'attaque simplifié
                        attacked = False
                        for pion_row in range(1, 9):
                            for pion_col in range(1, 9):
                                if pawn_grid[pion_row][pion_col] != 0:
                                    cell_color = board_grid[pion_row][pion_col]
                                    
                                    if cell_color == 3:  # Roi
                                        if abs(test_row - pion_row) <= 1 and abs(test_col - pion_col) <= 1:
                                            if test_row != pion_row or test_col != pion_col:
                                                attacked = True
                                                break
                                    elif cell_color == 4:  # Tour
                                        if test_row == pion_row or test_col == pion_col:
                                            if test_row == pion_row:
                                                start_col = min(test_col, pion_col) + 1
                                                end_col = max(test_col, pion_col)
                                                path_clear = True
                                                for c in range(start_col, end_col):
                                                    if pawn_grid[test_row][c] != 0 or board_grid[test_row][c] == 4:
                                                        path_clear = False
                                                        break
                                                if path_clear:
                                                    attacked = True
                                                    break
                                            else:
                                                start_row = min(test_row, pion_row) + 1
                                                end_row = max(test_row, pion_row)
                                                path_clear = True
                                                for r in range(start_row, end_row):
                                                    if pawn_grid[r][test_col] != 0 or board_grid[r][test_col] == 4:
                                                        path_clear = False
                                                        break
                                                if path_clear:
                                                    attacked = True
                                                    break
                                    elif cell_color == 1:  # Fou
                                        dr, dc = test_row - pion_row, test_col - pion_col
                                        if abs(dr) == abs(dc) and dr != 0:
                                            step_r = 1 if dr > 0 else -1
                                            step_c = 1 if dc > 0 else -1
                                            temp_r, temp_c = pion_row + step_r, pion_col + step_c
                                            path_clear = True
                                            while temp_r != test_row and temp_c != test_col:
                                                if pawn_grid[temp_r][temp_c] != 0 or board_grid[temp_r][temp_c] == 1:
                                                    path_clear = False
                                                    break
                                                temp_r += step_r
                                                temp_c += step_c
                                            if path_clear:
                                                attacked = True
                                                break
                                    elif cell_color == 2:  # Cavalier
                                        dr, dc = abs(test_row - pion_row), abs(test_col - pion_col)
                                        if (dr == 2 and dc == 1) or (dr == 1 and dc == 2):
                                            attacked = True
                                            break
                            if attacked:
                                break
                        if not attacked:
                            can_play = True
                            break
                if can_play:
                    break
            
            if not can_play:
                game_over = True
                game_ended = True
                winner = opponent_player
                victory_shown = False
                network_manager.send_message("victory", {"winner": winner})
        
        # MOUVEMENTS POSSIBLES
        if (selected_pawn and possible_moves and not game_over and 
            current_player == my_player and current_game_mode in [0, 1]):
            draw_simple_moves(screen, possible_moves, board_x, board_y, cell_size, current_game_mode)
        
        # VICTOIRE - AFFICHAGE DÉFINITIF ET PERSISTANT
        if game_ended and not victory_shown:
            victory_shown = True  # Marquer comme affiché une seule fois
            print(f"🎯 Affichage victoire : Winner={winner}, My_player={my_player}")

        if victory_shown and game_ended:
            # Affichage spécial pour Congress
            if current_game_mode == 1 and winner > 0:
                player_color = DARK_RED if winner == 1 else DARK_BLUE
                from jeux.congress import highlight_connected_pawns
                connected_pawns_display = [(row-1, col-1) for row, col in connected_pawns]
                highlight_connected_pawns(screen, connected_pawns_display, board_x, board_y, cell_size, player_color)
            
            # Fond avec transparence COMPLET
            overlay = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Plus opaque
            screen.blit(overlay, (0, 0))
            
            # Message selon la situation
            if winner == 0:
                victory_text = "🔌 PARTIE INTERROMPUE"
                color = (255, 165, 0)  # Orange
                info_text = "Connexion perdue"
            elif winner == my_player:
                victory_text = "🏆 VICTOIRE ! 🏆"
                color = GREEN
                mode_names = ["Katarenga", "Congress", "Isolation"]
                info_text = f"Mode {mode_names[current_game_mode]} - Bien joué !"
            else:
                victory_text = "💀 DÉFAITE 💀"
                color = RED
                mode_names = ["Katarenga", "Congress", "Isolation"]
                info_text = f"Mode {mode_names[current_game_mode]} - Dommage..."
            
            # Polices
            font_big = pygame.font.Font(None, 72)  # Plus gros
            font_medium = pygame.font.Font(None, 36)
            
            # Texte principal
            text = font_big.render(victory_text, True, color)
            text_rect = text.get_rect(center=(current_width // 2, current_height // 2 - 60))
            
            # Texte d'information
            info_surface = font_medium.render(info_text, True, BLACK)
            info_rect = info_surface.get_rect(center=(current_width // 2, current_height // 2 - 10))
            
            # Boîte de message plus grande
            box_width = max(text_rect.width + 100, 500)
            box_height = 200
            box_rect = pygame.Rect(
                (current_width - box_width) // 2,
                (current_height - box_height) // 2 - 40,
                box_width,
                box_height
            )
            
            # Dessiner la boîte avec bordure épaisse
            pygame.draw.rect(screen, WHITE, box_rect)
            pygame.draw.rect(screen, color, box_rect, 6)  # Bordure plus épaisse
            
            # Dessiner les textes
            screen.blit(text, text_rect)
            screen.blit(info_surface, info_rect)
            
            # Boutons plus visibles
            btn_width = 140  # Plus larges
            btn_height = 45   # Plus hauts
            btn_spacing = 40
            
            rejouer_btn = pygame.Rect(
                current_width // 2 - btn_width - btn_spacing // 2,
                current_height // 2 + 50,
                btn_width,
                btn_height
            )
            
            quitter_btn = pygame.Rect(
                current_width // 2 + btn_spacing // 2,
                current_height // 2 + 50,
                btn_width,
                btn_height
            )
            
            # Dessiner les boutons avec dégradé
            pygame.draw.rect(screen, BLUE, rejouer_btn)
            pygame.draw.rect(screen, RED, quitter_btn)
            pygame.draw.rect(screen, BLACK, rejouer_btn, 3)  # Bordure noire
            pygame.draw.rect(screen, BLACK, quitter_btn, 3)
            
            # Textes des boutons plus grands
            btn_font = pygame.font.Font(None, 36)
            rejouer_text = btn_font.render("REJOUER", True, WHITE)
            quitter_text = btn_font.render("QUITTER", True, WHITE)
            
            screen.blit(rejouer_text, rejouer_text.get_rect(center=rejouer_btn.center))
            screen.blit(quitter_text, quitter_text.get_rect(center=quitter_btn.center))
        
        # INFOS
        if not game_over:
            if current_player == my_player:
                turn_text = font.render("Votre tour", True, DARK_RED if my_player == 1 else DARK_BLUE)
            else:
                turn_text = font.render("Tour adversaire", True, DARK_RED if opponent_player == 1 else DARK_BLUE)
            screen.blit(turn_text, (current_width - 200, 20))
        
        mode_text = font.render(f"Mode: {['Katarenga', 'Congress', 'Isolation'][current_game_mode]}", True, BLACK)
        screen.blit(mode_text, (current_width - 200, 50))
        
        # Bouton abandonner
        abandon_btn = pygame.Rect(20, 20, 100, 30)
        pygame.draw.rect(screen, RED, abandon_btn)
        abandon_text = font.render("Abandonner", True, WHITE)
        screen.blit(abandon_text, abandon_text.get_rect(center=abandon_btn.center))
        
        # ÉVÉNEMENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Envoyer déconnexion avant de quitter
                if network_manager.is_connected:
                    network_manager.send_message("disconnect", {})
                network_manager.disconnect()
                return
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Abandonner
                if abandon_btn.collidepoint(event.pos):
                    # Envoyer déconnexion avant d'abandonner
                    if network_manager.is_connected:
                        network_manager.send_message("disconnect", {})
                    network_manager.disconnect()
                    return
                
                # Victoire - boutons (CORRIGÉ FINAL)
                if victory_shown and game_ended:
                    if rejouer_btn.collidepoint(event.pos):
                        print("🔄 REDÉMARRAGE → Menu de connexion réseau")
                        
                        # Réinitialisation complète avant déconnexion
                        game_over = False
                        game_ended = False
                        victory_shown = False
                        victory_message_sent = False
                        winner = 0
                        selected_pawn = None
                        possible_moves = []
                        
                        # Envoyer déconnexion proprement
                        if network_manager.is_connected:
                            network_manager.send_message("disconnect", {})
                            pygame.time.wait(100)  # Laisser le temps d'envoyer
                        
                        network_manager.disconnect()
                        
                        # Réinitialiser variables globales
                        import plateau.game_modes
                        plateau.game_modes.GLOBAL_SELECTED_GAME = current_game_mode
                        
                        # Attendre un peu avant de relancer
                        pygame.time.wait(200)
                        
                        # CORRECTION : Retour au menu de connexion réseau
                        from réseaux.network_menu import show_network_menu
                        return show_network_menu(screen)
                        
                    elif quitter_btn.collidepoint(event.pos):
                        print("🚪 RETOUR AU HUB PRINCIPAL")
                        
                        # Envoyer déconnexion proprement
                        if network_manager.is_connected:
                            network_manager.send_message("disconnect", {})
                            pygame.time.wait(100)
                        
                        network_manager.disconnect()
                        
                        # CORRECTION : Retour au hub principal
                        return  # Cela retourne vers hub.py
                
                # JEU - SEULEMENT si partie active
                if (not victory_shown and not game_ended and not game_over and 
                    current_player == my_player and not animation.is_moving()):
                    mouse_x, mouse_y = event.pos
                    
                    if (board_x <= mouse_x < board_x + board_size and 
                        board_y <= mouse_y < board_y + board_size):
                        
                        col = (mouse_x - board_x) // cell_size
                        row = (mouse_y - board_y) // cell_size
                        
                        # Coordonnées grille selon le mode
                        if current_game_mode == 0:  # Katarenga
                            grid_row, grid_col = row, col
                        else:  # Congress et Isolation
                            grid_row = row + 1
                            grid_col = col + 1
                        
                        # ISOLATION - PLACEMENT
                        if current_game_mode == 2:
                            if (1 <= grid_row <= 8 and 1 <= grid_col <= 8 and 
                                pawn_grid[grid_row][grid_col] == 0):
                                
                                # Test d'attaque simplifié
                                can_place = True
                                for pion_row in range(1, 9):
                                    for pion_col in range(1, 9):
                                        if pawn_grid[pion_row][pion_col] != 0:
                                            cell_color = board_grid[pion_row][pion_col]
                                            
                                            if cell_color == 3:  # Roi
                                                if (abs(grid_row - pion_row) <= 1 and 
                                                    abs(grid_col - pion_col) <= 1 and 
                                                    (grid_row != pion_row or grid_col != pion_col)):
                                                    can_place = False
                                                    break
                                            elif cell_color == 4:  # Tour
                                                if grid_row == pion_row or grid_col == pion_col:
                                                    if grid_row == pion_row:
                                                        start_col = min(grid_col, pion_col) + 1
                                                        end_col = max(grid_col, pion_col)
                                                        path_clear = True
                                                        for c in range(start_col, end_col):
                                                            if pawn_grid[grid_row][c] != 0 or board_grid[grid_row][c] == 4:
                                                                path_clear = False
                                                                break
                                                        if path_clear:
                                                            can_place = False
                                                            break
                                                    else:
                                                        start_row = min(grid_row, pion_row) + 1
                                                        end_row = max(grid_row, pion_row)
                                                        path_clear = True
                                                        for r in range(start_row, end_row):
                                                            if pawn_grid[r][grid_col] != 0 or board_grid[r][grid_col] == 4:
                                                                path_clear = False
                                                                break
                                                        if path_clear:
                                                            can_place = False
                                                            break
                                            elif cell_color == 1:  # Fou
                                                dr, dc = grid_row - pion_row, grid_col - pion_col
                                                if abs(dr) == abs(dc) and dr != 0:
                                                    step_r = 1 if dr > 0 else -1
                                                    step_c = 1 if dc > 0 else -1
                                                    temp_r, temp_c = pion_row + step_r, pion_col + step_c
                                                    path_clear = True
                                                    while temp_r != grid_row and temp_c != grid_col:
                                                        if pawn_grid[temp_r][temp_c] != 0 or board_grid[temp_r][temp_c] == 1:
                                                            path_clear = False
                                                            break
                                                        temp_r += step_r
                                                        temp_c += step_c
                                                    if path_clear:
                                                        can_place = False
                                                        break
                                            elif cell_color == 2:  # Cavalier
                                                dr = abs(grid_row - pion_row)
                                                dc = abs(grid_col - pion_col)
                                                if (dr == 2 and dc == 1) or (dr == 1 and dc == 2):
                                                    can_place = False
                                                    break
                                    if not can_place:
                                        break
                                
                                if can_place:
                                    pawn_grid[grid_row][grid_col] = current_player
                                    send_placement((grid_row, grid_col))
                                    
                                    from jeux.isolation import check_isolation_victory
                                    game_over_temp, winner_temp = check_isolation_victory(pawn_grid, current_player, board_grid)
                                    
                                    if game_over_temp:
                                        game_over = True
                                        game_ended = True
                                        winner = winner_temp
                                        victory_shown = False
                                        network_manager.send_message("victory", {"winner": winner})
                                    else:
                                        current_player = opponent_player
                        
                        # KATARENGA ET CONGRESS - DÉPLACEMENT
                        elif current_game_mode in [0, 1]:
                            if current_game_mode == 0:
                                valid = 0 <= grid_row < 10 and 0 <= grid_col < 10
                            else:
                                valid = 1 <= grid_row <= 8 and 1 <= grid_col <= 8
                            
                            if valid:
                                if selected_pawn:
                                    selected_row, selected_col = selected_pawn
                                    
                                    if (grid_row, grid_col) in possible_moves:
                                        # Katarenga - camps
                                        if current_game_mode == 0:
                                            from jeux.katarenga import get_camp_positions, place_in_camp, check_katarenga_victory, is_camp_occupied
                                            camp_positions = get_camp_positions(current_player)
                                            
                                            if (grid_row, grid_col) in camp_positions:
                                                # CORRECTION CRITIQUE : Vérifier si le camp est déjà occupé AVANT de tenter le placement
                                                if not is_camp_occupied(grid_row, grid_col, current_player):
                                                    if place_in_camp(grid_row, grid_col, pawn_grid, current_player):
                                                        pawn_grid[selected_row][selected_col] = 0
                                                        send_move((selected_row, selected_col), (grid_row, grid_col))
                                                        winner = check_katarenga_victory()
                                                        if winner > 0 and not victory_message_sent:
                                                            game_over = True
                                                            game_ended = True
                                                            victory_shown = False
                                                            victory_message_sent = True
                                                            print(f"🏆 Victoire Katarenga par placement: Joueur {winner}")
                                                            network_manager.send_message("victory", {"winner": winner})
                                                        else:
                                                            # CORRECTION : Changer le tour après placement dans un camp
                                                            current_player = opponent_player
                                                            print(f"Tour passé à joueur {current_player} après placement camp")
                                                        selected_pawn = None
                                                        possible_moves = []
                                                        continue
                                                else:
                                                    # Camp déjà occupé - annuler la sélection
                                                    print("❌ Camp déjà occupé !")
                                                    selected_pawn = None
                                                    possible_moves = []
                                                    continue
                                        
                                        # Mouvement normal
                                        animation.start_move(
                                            selected_row, selected_col, grid_row, grid_col,
                                            board_x, board_y, cell_size,
                                            pawn_grid[selected_row][selected_col]
                                        )
                                        
                                        send_move((selected_row, selected_col), (grid_row, grid_col))
                                        
                                        # Congress - exécution immédiate
                                        if current_game_mode == 1:
                                            pawn_grid[grid_row][grid_col] = pawn_grid[selected_row][selected_col]
                                            pawn_grid[selected_row][selected_col] = 0
                                            
                                            # Vérifier victoire
                                            from jeux.congress import check_victory
                                            temp_grid = [[0 for _ in range(8)] for _ in range(8)]
                                            for row in range(1, 9):
                                                for col in range(1, 9):
                                                    temp_grid[row-1][col-1] = pawn_grid[row][col]
                                            
                                            winner, connected_pawns_temp = check_victory(temp_grid)
                                            if winner > 0:
                                                connected_pawns = [(row+1, col+1) for row, col in connected_pawns_temp]
                                                game_over = True
                                                game_ended = True
                                                victory_shown = False
                                                network_manager.send_message("victory", {"winner": winner})
                                            else:
                                                current_player = opponent_player
                                            

                                            # Pas d'animation pour Congress
                                            animation.moving_pawn = None
                                            animation.pending_move = None
                                        else:
                                            # Animation pour Katarenga
                                            animation.pending_move = {
                                                'from': (selected_row, selected_col),
                                                'to': (grid_row, grid_col),
                                                'pawn_color': pawn_grid[selected_row][selected_col]
                                            }
                                        
                                        selected_pawn = None
                                        possible_moves = []
                                    
                                    # Sélectionner autre pion
                                    elif pawn_grid[grid_row][grid_col] == my_player:
                                        selected_pawn = (grid_row, grid_col)
                                        possible_moves = get_valid_moves(grid_row, grid_col, board_grid, pawn_grid, current_game_mode)
                                    
                                    # Annuler
                                    else:
                                        selected_pawn = None
                                        possible_moves = []
                                
                                # Sélectionner pion
                                else:
                                    if pawn_grid[grid_row][grid_col] == my_player:
                                        selected_pawn = (grid_row, grid_col)
                                        possible_moves = get_valid_moves(grid_row, grid_col, board_grid, pawn_grid, current_game_mode)
        
        # Vérifier connexion
        if not network_manager.is_connected and not game_over:
            game_over = True
            game_ended = True
            victory_shown = False
            # Pas de winner = "Partie interrompue"
        
        pygame.display.flip()
        clock.tick(60)
    
    # Envoyer déconnexion à la sortie
    if network_manager.is_connected:
        network_manager.send_message("disconnect", {})
    network_manager.disconnect()


# FONCTIONS SIMPLES

def draw_simple_pawns(screen, pawn_grid, board_x, board_y, cell_size, selected_pawn, animation, current_game_mode):
    """Dessine les pions - VERSION CORRIGÉE"""
    DARK_RED = Colors.DARK_RED
    DARK_BLUE = Colors.DARK_BLUE
    BLACK = Colors.BLACK
    
    moving_pos = animation.get_current_pos()
    moving_pawn_info = animation.moving_pawn
    
    # Zone de dessin selon le mode
    if current_game_mode == 0:  # Katarenga - plateau complet
        grid_range = range(10)
        offset_row, offset_col = 0, 0
    else:  # Congress et Isolation - zone 8x8
        grid_range = range(1, 9)
        offset_row, offset_col = 1, 1  # Offset pour l'affichage
    
    for row in grid_range:
        for col in grid_range:
            if pawn_grid[row][col] > 0:
                # Skip pion en mouvement
                if (moving_pawn_info and 
                    moving_pawn_info[0] == row and moving_pawn_info[1] == col):
                    continue
                
                pawn_color = DARK_RED if pawn_grid[row][col] == 1 else DARK_BLUE
                
                # Position d'affichage
                display_row = row - offset_row
                display_col = col - offset_col
                
                center = (
                    board_x + display_col * cell_size + cell_size // 2,
                    board_y + display_row * cell_size + cell_size // 2
                )
                
                radius = cell_size // 3
                
                # Sélection
                if selected_pawn and selected_pawn == (row, col):
                    pygame.draw.circle(screen, (255, 255, 0), center, radius + 4, 3)
                
                # Pion
                pygame.draw.circle(screen, pawn_color, center, radius)
                pygame.draw.circle(screen, BLACK, center, radius, 2)
    
    # Pion en mouvement
    if moving_pos and moving_pawn_info and animation.moving_pawn_color:
        pawn_color = DARK_RED if animation.moving_pawn_color == 1 else DARK_BLUE
        radius = cell_size // 3
        pygame.draw.circle(screen, pawn_color, moving_pos, radius)
        pygame.draw.circle(screen, BLACK, moving_pos, radius, 2)


def draw_simple_moves(screen, possible_moves, board_x, board_y, cell_size, current_game_mode):
    """Dessine les mouvements possibles - CERCLES NOIRS"""
    BLACK = (0, 0, 0)
    
    for move_row, move_col in possible_moves:
        # Coordonnées d'affichage selon le mode
        if current_game_mode == 0:  # Katarenga
            display_row, display_col = move_row, move_col
        else:  # Congress et Isolation
            display_row = move_row - 1  # Offset pour l'affichage
            display_col = move_col - 1
        
        # Centre case
        center_x = board_x + display_col * cell_size + cell_size // 2
        center_y = board_y + display_row * cell_size + cell_size // 2
        
        # Cercle noir
        radius = cell_size // 8
        pygame.draw.circle(screen, BLACK, (center_x, center_y), radius)


def draw_isolation_crosses(screen, pawn_grid, board_grid, board_x, board_y, cell_size):
    """Dessine les croix Isolation"""
    forbidden = set()
    
    # Positions interdites
    for pion_row in range(1, 9):
        for pion_col in range(1, 9):
            if pawn_grid[pion_row][pion_col] != 0:
                cell_color = board_grid[pion_row][pion_col]
                
                if cell_color == 3:  # Roi
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            new_row, new_col = pion_row + dr, pion_col + dc
                            if 1 <= new_row <= 8 and 1 <= new_col <= 8:
                                forbidden.add((new_row, new_col))
                
                elif cell_color == 4:  # Tour
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        new_row, new_col = pion_row + dr, pion_col + dc
                        while 1 <= new_row <= 8 and 1 <= new_col <= 8:
                            forbidden.add((new_row, new_col))
                            if pawn_grid[new_row][new_col] != 0:
                                break
                            if board_grid[new_row][new_col] == 4:
                                break
                            new_row, new_col = new_row + dr, new_col + dc
                
                elif cell_color == 1:  # Fou
                    for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                        new_row, new_col = pion_row + dr, pion_col + dc
                        while 1 <= new_row <= 8 and 1 <= new_col <= 8:
                            forbidden.add((new_row, new_col))
                            if pawn_grid[new_row][new_col] != 0:
                                break
                            if board_grid[new_row][new_col] == 1:
                                break
                            new_row, new_col = new_row + dr, new_col + dc
                
                elif cell_color == 2:  # Cavalier
                    moves = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
                    for dr, dc in moves:
                        new_row, new_col = pion_row + dr, pion_col + dc
                        if 1 <= new_row <= 8 and 1 <= new_col <= 8:
                            forbidden.add((new_row, new_col))
    
    # Dessiner croix sur les positions interdites vides
    for row, col in forbidden:
        if pawn_grid[row][col] == 0:
            # Coordonnées d'affichage avec offset
            display_row = row - 1
            display_col = col - 1
            
            x = board_x + display_col * cell_size
            y = board_y + display_row * cell_size
            margin = cell_size // 4
            
            pygame.draw.line(screen, (0, 0, 0), 
                (x + margin, y + margin), 
                (x + cell_size - margin, y + cell_size - margin), 6)
            pygame.draw.line(screen, (0, 0, 0), 
                (x + cell_size - margin, y + margin), 
                (x + margin, y + cell_size - margin), 6)