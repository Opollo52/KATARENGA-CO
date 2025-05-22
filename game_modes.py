import pygame

# Variables globales pour garder le mode de jeu et l'adversaire
GLOBAL_SELECTED_GAME = 0 
GLOBAL_SELECTED_OPPONENT = 0
FIRST_RUN = True

def show_game_modes(screen):
    """
    Affiche la fenêtre de sélection des modes de jeu.
    """
    global GLOBAL_SELECTED_GAME, GLOBAL_SELECTED_OPPONENT, FIRST_RUN
    
    # Utiliser les dimensions actuelles de l'écran pour un meilleur centrage
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    pygame.display.set_caption("Sélection du mode de jeu")
    
    WHITE = (255, 255, 255)
    BLUE = (50, 100, 200)  
    RED = (255, 50, 50)  
    BLACK = (0, 0, 0)
    GREEN = (50, 180, 50)
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 42)
    
    # Configuration de l'écran
    screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
    
    # Options disponibles
    game_types = ["Katarenga", "Congress", "Isolation"]
    opponent_types = ["Ordi", "Local", "En ligne"]
    
    # Utiliser les sélections globales (qui sont mises à jour à chaque fois)
    selected_game = GLOBAL_SELECTED_GAME
    selected_opponent = GLOBAL_SELECTED_OPPONENT
    
    # Configuration des boutons - Réduction de la taille
    button_width = 130
    button_height = 50
    horizontal_spacing = 40
    vertical_spacing = 90
    
    # Calcul de la largeur totale des boutons et espaces
    total_width = (button_width * 3) + (horizontal_spacing * 2)
    
    # Calcul de la hauteur totale incluant tous les éléments
    play_button_height = 60
    title_height = 40
    info_text_height = 40
    selection_text_height = 30
    spacing_between_sections = 20
    
    total_height = (
        title_height + spacing_between_sections +  # Titre de la section jeu
        button_height + vertical_spacing +         # Boutons de jeu + espace
        title_height + spacing_between_sections +  # Titre de la section adversaire
        button_height + spacing_between_sections + # Boutons d'adversaire + espace
        selection_text_height + spacing_between_sections + # Texte de sélection
        play_button_height                         # Boutons jouer/retour
    )
    
    # Position de départ pour centrer verticalement tout le contenu
    start_y = (HEIGHT - total_height) // 2
    current_y = start_y
    
    # Position de départ pour centrer horizontalement les grilles de boutons
    start_x = (WIDTH - total_width) // 2
    
    # Position pour les titres des sections (centrage)
    game_title_y = current_y
    current_y += title_height + spacing_between_sections
    
    # Position pour les boutons de type de jeu
    game_buttons_y = current_y
    current_y += button_height + vertical_spacing
    
    # Position pour le titre de la section adversaire
    opponent_title_y = current_y
    current_y += title_height + spacing_between_sections
    
    # Position pour les boutons d'adversaire
    opponent_buttons_y = current_y
    current_y += button_height + spacing_between_sections
    
    # Position pour le texte de sélection actuelle
    selection_text_y = current_y
    current_y += selection_text_height + spacing_between_sections
    
    # Position pour les boutons Jouer et Retour
    button_row_y = current_y
    
    # Création des boutons de type de jeu (première ligne)
    game_buttons = []
    for col in range(3):
        x = start_x + col * (button_width + horizontal_spacing)
        y = game_buttons_y
        rect = pygame.Rect(x, y, button_width, button_height)
        game_buttons.append(rect)
    
    # Création des boutons d'adversaire (deuxième ligne)
    opponent_buttons = []
    for col in range(3):
        x = start_x + col * (button_width + horizontal_spacing)
        y = opponent_buttons_y
        rect = pygame.Rect(x, y, button_width, button_height)
        opponent_buttons.append(rect)
    
    # Bouton Jouer et Retour sur la même ligne - centrage horizontal
    play_button_width = 180
    play_button_height = 60
    back_button_width = 180
    back_button_height = 60
    
    buttons_total_width = play_button_width + 40 + back_button_width  # 40px d'espacement entre les boutons
    buttons_start_x = (WIDTH - buttons_total_width) // 2
    
    play_button = pygame.Rect(
        buttons_start_x,
        button_row_y,
        play_button_width, 
        play_button_height
    )
    
    back_button = pygame.Rect(
        buttons_start_x + play_button_width + 40,
        button_row_y,
        back_button_width, 
        back_button_height
    )
    
    def draw_centered_text(text, rect, color):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
    
    def draw_section_title(text, y):
        title_surf = title_font.render(text, True, BLACK)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, y))
        screen.blit(title_surf, title_rect)
    
    running = True
    while running:
        screen.fill(WHITE)
        
        # Afficher les titres des sections
        draw_section_title("Choisissez votre jeu", game_title_y)
        draw_section_title("Choisissez votre adversaire", opponent_title_y)
        
        # Dessiner les boutons de type de jeu avec le bouton sélectionné en rouge
        for i, rect in enumerate(game_buttons):
            color = RED if i == selected_game else BLUE
            pygame.draw.rect(screen, color, rect)
            draw_centered_text(game_types[i], rect, WHITE)
        
        # Dessiner les boutons d'adversaire avec le bouton sélectionné en rouge
        for i, rect in enumerate(opponent_buttons):
            color = RED if i == selected_opponent else BLUE
            pygame.draw.rect(screen, color, rect)
            draw_centered_text(opponent_types[i], rect, WHITE)
        
        # Dessiner le bouton Jouer
        pygame.draw.rect(screen, GREEN, play_button)
        draw_centered_text("Jouer", play_button, WHITE)
        
        # Dessiner le bouton Retour
        pygame.draw.rect(screen, BLUE, back_button)
        draw_centered_text("Retour", back_button, WHITE)
        
        # Si c'est la première exécution, afficher un message spécial
        if FIRST_RUN:
            first_run_text = "Mode par défaut sélectionné"
            info_text = font.render(first_run_text, True, BLACK)
            info_rect = info_text.get_rect(center=(WIDTH // 2, start_y - 30))
            screen.blit(info_text, info_rect)
        
        # Afficher la sélection actuelle
        current_selection = f"Mode actuel : {game_types[selected_game]} - {opponent_types[selected_opponent]}"
        selection_text = font.render(current_selection, True, BLACK)
        selection_rect = selection_text.get_rect(center=(WIDTH // 2, selection_text_y))
        screen.blit(selection_text, selection_rect)
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier si un bouton de type de jeu a été cliqué
                for i, rect in enumerate(game_buttons):
                    if rect.collidepoint(event.pos):
                        selected_game = i
                        GLOBAL_SELECTED_GAME = i  # Mettre à jour la variable globale
                        FIRST_RUN = False  # Ce n'est plus le premier lancement
                
                # Vérifier si un bouton d'adversaire a été cliqué
                for i, rect in enumerate(opponent_buttons):
                    if rect.collidepoint(event.pos):
                        selected_opponent = i
                        GLOBAL_SELECTED_OPPONENT = i  # Mettre à jour la variable globale
                        FIRST_RUN = False  # Ce n'est plus le premier lancement
                
                # Vérifier si le bouton Jouer a été cliqué
                if play_button.collidepoint(event.pos):
                    # Lancer la configuration de la partie avec le mode sélectionné
                    from game_setup import show_game_setup
                    running = False
                    show_game_setup(screen)
                
                # Vérifier si le bouton Retour a été cliqué
                if back_button.collidepoint(event.pos):
                    # Enregistrer les préférences de jeu ici si nécessaire
                    print(f"Mode sélectionné: {game_types[selected_game]} - {opponent_types[selected_opponent]}")
                    running = False
        
        pygame.display.flip()