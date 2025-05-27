import pygame
import os
import sys
import time
from assets.colors import Colors
from game_board import create_game_board, initialize_pawns_for_game_mode, Animation, draw_animated_pawns
from pawn import get_valid_moves, highlight_possible_moves
from congress import check_victory, highlight_connected_pawns, display_victory_message

def start_network_game(screen, network_manager):
    """
    Lance le jeu en réseau avec configuration des quadrants par joueur
    """
    print("=== DÉBUT NOUVELLE PARTIE RÉSEAU ===")
    
    pygame.display.set_caption("Partie en réseau")
    
    # Couleurs et ressources
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
    
    images = {}
    images[1] = pygame.image.load(os.path.join(PATH, "assets", "img", "yellow.png"))  
    images[2] = pygame.image.load(os.path.join(PATH, "assets", "img", "green.png"))  
    images[3] = pygame.image.load(os.path.join(PATH, "assets", "img", "blue.png"))   
    images[4] = pygame.image.load(os.path.join(PATH, "assets", "img", "red.png"))
    
    frame_image = pygame.image.load(os.path.join(PATH, "assets", "img", "frame.png"))
    
    # SYNCHRONISATION DU MODE DE JEU
    import game_modes
    local_game_mode = game_modes.GLOBAL_SELECTED_GAME
    
    if network_manager.is_server:
        print(f"Serveur : Envoi du mode de jeu {local_game_mode}")
        # L'hôte envoie son mode de jeu au client
        network_manager.send_message("game_mode", {"mode": local_game_mode})
        current_game_mode = local_game_mode
        my_player = 1
        opponent_player = 2
    else:
        print("Client : En attente du mode de jeu du serveur...")
        # Le client attend de recevoir le mode de jeu du serveur
        mode_received = False
        timeout = time.time() + 10  # Timeout de 10 secondes
        
        while not mode_received and time.time() < timeout:
            messages = network_manager.get_messages()
            for message in messages:
                if message['type'] == 'game_mode':
                    current_game_mode = message['data']['mode']
                    print(f"Client : Mode de jeu reçu du serveur : {current_game_mode}")
                    mode_received = True
                    break
            
            if not mode_received:
                pygame.time.wait(100)  # Attendre un peu avant de vérifier à nouveau
        
        if not mode_received:
            print("ERREUR : Impossible de recevoir le mode de jeu du serveur")
            return
            
        my_player = 2
        opponent_player = 1
    
    print(f"Mode de jeu synchronisé: {current_game_mode}")
    
    # Lancer la configuration des quadrants par chaque joueur
    from network_quadrant_setup import show_network_quadrant_setup
    quadrants_data = show_network_quadrant_setup(screen, network_manager, network_manager.is_server)
    
    if quadrants_data is None:
        print("Configuration annulée")
        return
    
    print(f"Configuration terminée - Plateau assemblé")
    
    # Créer le plateau et initialiser les pions
    board_grid = create_game_board(quadrants_data)
    pawn_grid = initialize_pawns_for_game_mode(current_game_mode)
    animation = Animation()
    
    # Variables de jeu
    selected_pawn = None
    possible_moves = []
    current_player = 1  # Toujours commencer par le joueur Rouge
    game_over = False
    winner = 0
    connected_pawns = []
    
    print(f"=== PARTIE INITIALISÉE - Mode: {current_game_mode}, Mon joueur: {my_player} ===")
    
    # Interface
    font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    
    def process_network_messages():
        """Traite les messages reçus du réseau"""
        nonlocal pawn_grid, current_player, game_over, winner, connected_pawns, selected_pawn, possible_moves
        
        messages = network_manager.get_messages()
        for message in messages:
            if message['type'] == 'move':
                move_data = message['data']
                from_pos = move_data['from']
                to_pos = move_data['to']
                
                print(f"Mouvement reçu: {from_pos} -> {to_pos}")
                
                # Démarrer l'animation pour le mouvement de l'adversaire
                animation.start_move(
                    from_pos[0], from_pos[1], to_pos[0], to_pos[1],
                    board_x, board_y, cell_size,
                    pawn_grid[from_pos[0]][from_pos[1]]
                )
                
                # Stocker le mouvement pour l'exécution après l'animation
                animation.pending_move = {
                    'from': from_pos,
                    'to': to_pos,
                    'pawn_color': pawn_grid[from_pos[0]][from_pos[1]]
                }
                
                # Réinitialiser la sélection
                selected_pawn = None
                possible_moves = []
            
            elif message['type'] == 'disconnect':
                print("Adversaire déconnecté - Victoire par forfait")
                game_over = True
                winner = my_player
    
    def send_move(from_pos, to_pos):
        """Envoie un mouvement à l'adversaire"""
        print(f"Envoi du mouvement: {from_pos} -> {to_pos}")
        network_manager.send_message("move", {
            "from": from_pos,
            "to": to_pos,
            "player": my_player
        })
    
    # Boucle principale de jeu
    running = True
    while running:
        # Traiter les messages réseau
        if not game_over:
            process_network_messages()
        
        # Récupérer les dimensions actuelles de la fenêtre
        current_width, current_height = screen.get_size()
        
        # Calculer la taille des cellules
        cell_size = min(current_width, current_height) // 12
        
        # Redimensionner les images
        for key in images:
            images[key] = pygame.transform.scale(images[key], (cell_size, cell_size))
        
        # Taille et position du plateau
        board_size = 8 * cell_size
        board_x = (current_width - board_size) // 2
        board_y = (current_height - board_size) // 2
        
        # Bouton retour
        back_button = pygame.Rect(20, 20, 100, 30)
        
        # Affichage du fond
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))
        
        # Dessiner le cadre du plateau
        if frame_image:
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
                
                if cell_value in images:
                    screen.blit(images[cell_value], cell_rect)
                
                pygame.draw.rect(screen, BLACK, cell_rect, 2)
        
        # Dessiner les pions avec animations
        draw_animated_pawns(screen, pawn_grid, board_x, board_y, cell_size, selected_pawn, animation)
        
        # Traitement de l'animation
        if not animation.is_moving() and animation.has_pending_move():
            winner_result, connected_result, game_over_result = animation.execute_pending_move(pawn_grid, current_game_mode)
            if winner_result is not None:
                winner = winner_result
                connected_pawns = connected_result
                game_over = game_over_result
                print(f"Jeu terminé - Gagnant: {winner}")
            
            if not game_over:
                current_player = 3 - current_player
        
        # Dessiner les mouvements possibles (seulement pour le joueur actuel)
        if (selected_pawn and possible_moves and not game_over and 
            not animation.is_moving() and current_player == my_player):
            highlight_possible_moves(screen, possible_moves, board_x, board_y, cell_size)
        
        # Affichage de la victoire
        if game_over and winner > 0:
            if current_game_mode == 1:  # Congress
                player_color = DARK_RED if winner == 1 else DARK_BLUE
                highlight_connected_pawns(screen, connected_pawns, board_x, board_y, cell_size, player_color)
                display_victory_message(screen, winner)
            else:
                # Affichage de victoire pour tous les modes
                victory_message = ""
                if winner == my_player:
                    victory_message = "Vous avez gagné !"
                    if not network_manager.is_connected:
                        victory_message = "Victoire par forfait !"
                    victory_color = GREEN
                else:
                    victory_message = "Victoire de l'adversaire"
                    victory_color = RED
                
                # Afficher le message de victoire
                font_large = pygame.font.Font(None, 48)
                victory_text = font_large.render(victory_message, True, victory_color)
                victory_rect = victory_text.get_rect(center=(current_width // 2, current_height // 2))
                
                # Fond semi-transparent
                padding = 20
                bg_rect = pygame.Rect(
                    victory_rect.left - padding,
                    victory_rect.top - padding,
                    victory_rect.width + 2 * padding,
                    victory_rect.height + 2 * padding
                )
                bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                bg_surface.fill((0, 0, 0, 150))
                screen.blit(bg_surface, bg_rect)
                
                # Bordure et texte
                pygame.draw.rect(screen, victory_color, bg_rect, 3)
                screen.blit(victory_text, victory_rect)
        
        # Afficher les informations de jeu
        if not game_over:
            # Statut du tour
            if current_player == my_player:
                turn_text = font.render(f"Votre tour ({'Rouge' if my_player == 1 else 'Bleu'})", True, DARK_RED if my_player == 1 else DARK_BLUE)
            else:
                turn_text = font.render(f"Tour de l'adversaire ({'Rouge' if opponent_player == 1 else 'Bleu'})", True, DARK_RED if opponent_player == 1 else DARK_BLUE)
            
            screen.blit(turn_text, (current_width - 250, 20))
            
            # Statut de la connexion
            connection_status = "Connecté" if network_manager.is_connected else "Déconnecté"
            connection_color = GREEN if network_manager.is_connected else RED
            conn_text = font.render(f"Réseau: {connection_status}", True, connection_color)
            screen.blit(conn_text, (current_width - 250, 50))
        
        # Afficher le mode de jeu
        mode_names = ["Katarenga", "Congress", "Isolation"]
        mode_text = font.render(f"Mode: {mode_names[current_game_mode]}", True, BLACK)
        screen.blit(mode_text, (current_width - 250, 80))
        
        # Bouton abandonner
        text_width, text_height = font.size("Abandonner")
        back_button = pygame.Rect(back_button.x, back_button.y, text_width + 20, text_height + 10)
        pygame.draw.rect(screen, RED, back_button)
        back_text = font.render("Abandonner", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, back_text_rect)
        
        # Traitement des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                network_manager.send_message("disconnect", {"reason": "quit"})
                network_manager.disconnect()
                return
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    network_manager.send_message("disconnect", {"reason": "quit"})
                    network_manager.disconnect()
                    return
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Bouton retour
                if back_button.collidepoint(event.pos):
                    network_manager.send_message("disconnect", {"reason": "quit"})
                    network_manager.disconnect()
                    return
                
                # Jeu - seulement si c'est le tour du joueur
                if (not game_over and current_player == my_player and not animation.is_moving()):
                    mouse_x, mouse_y = event.pos
                    
                    # Vérifier si le clic est sur le plateau
                    if (board_x <= mouse_x < board_x + board_size and 
                        board_y <= mouse_y < board_y + board_size):
                        
                        col = (mouse_x - board_x) // cell_size
                        row = (mouse_y - board_y) // cell_size
                        
                        # Si un pion est déjà sélectionné
                        if selected_pawn:
                            selected_row, selected_col = selected_pawn
                            
                            # Vérifier si le mouvement est valide
                            if (row, col) in possible_moves:
                                # Démarrer l'animation
                                animation.start_move(
                                    selected_row, selected_col, row, col, 
                                    board_x, board_y, cell_size, 
                                    pawn_grid[selected_row][selected_col]
                                )
                                
                                # Envoyer le mouvement à l'adversaire
                                send_move((selected_row, selected_col), (row, col))
                                
                                # Stocker le mouvement pour l'exécution après l'animation
                                animation.pending_move = {
                                    'from': (selected_row, selected_col),
                                    'to': (row, col),
                                    'pawn_color': pawn_grid[selected_row][selected_col]
                                }
                                
                                # Réinitialiser la sélection
                                selected_pawn = None
                                possible_moves = []
                            
                            # Sélectionner un autre pion du même joueur
                            elif pawn_grid[row][col] == my_player:
                                selected_pawn = (row, col)
                                # CORRECTION: Utiliser le mode synchronisé
                                possible_moves = get_valid_moves(row, col, board_grid, pawn_grid, current_game_mode)
                            
                            # Annuler la sélection
                            else:
                                selected_pawn = None
                                possible_moves = []
                        
                        # Aucun pion sélectionné - sélectionner un pion du joueur
                        else:
                            if pawn_grid[row][col] == my_player:
                                selected_pawn = (row, col)
                                # CORRECTION: Utiliser le mode synchronisé
                                possible_moves = get_valid_moves(row, col, board_grid, pawn_grid, current_game_mode)
        
        # Vérifier si la connexion est toujours active
        if not network_manager.is_connected and not game_over:
            game_over = True
            winner = my_player
            print("Connexion perdue - Victoire par forfait")
        
        pygame.display.flip()
        clock.tick(60)
    
    print("=== FIN DE PARTIE RÉSEAU ===")
    # Nettoyer avant de quitter
    network_manager.disconnect()