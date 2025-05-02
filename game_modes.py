import pygame

# Variables globales pour mémoriser les choix de l'utilisateur
# Initialisation par défaut: Katarenga contre Ordi
GLOBAL_SELECTED_GAME = 0  # Index du jeu sélectionné (0: Katarenga, 1: Congress, 2: Isolation)
GLOBAL_SELECTED_OPPONENT = 0  # Index de l'adversaire sélectionné (0: Ordi, 1: Local, 2: En ligne)
FIRST_RUN = True  # Indique si c'est le premier lancement

def show_game_modes(screen):
    """
    Affiche la fenêtre de sélection des modes de jeu.
    Une ligne pour les types de jeu (Katarenga, Congress, Isolation)
    Une ligne pour les adversaires (Ordi, Local, En ligne)
    Fenêtre de 600x600 pixels
    """
    global GLOBAL_SELECTED_GAME, GLOBAL_SELECTED_OPPONENT, FIRST_RUN
    
    # Créer une nouvelle surface de 600x600 pixels
    mode_screen = pygame.Surface((600, 600))
    
    WHITE = (255, 255, 255)
    BLUE = (50, 100, 200)  # Couleur par défaut des boutons
    RED = (255, 50, 50)    # Couleur des boutons sélectionnés
    BLACK = (0, 0, 0)
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 42)
    
    # Configuration de l'écran
    screen_rect = mode_screen.get_rect()  # Utilise la taille de notre nouvelle surface
    
    # Options disponibles
    game_types = ["Katarenga", "Congress", "Isolation"]
    opponent_types = ["Ordi", "Local", "En ligne"]
    
    # Utiliser les sélections globales (qui sont mises à jour à chaque fois)
    selected_game = GLOBAL_SELECTED_GAME
    selected_opponent = GLOBAL_SELECTED_OPPONENT
    
    # Configuration des boutons - Réduction de la taille
    button_width = 130  # Réduit de 150 à 130
    button_height = 50  # Réduit de 60 à 50
    horizontal_spacing = 40  # Augmenté pour conserver l'espacement visuel
    vertical_spacing = 90  # Ajusté pour la nouvelle disposition
    
    # Calcul de la largeur totale des boutons et espaces
    total_width = (button_width * 3) + (horizontal_spacing * 2)
    
    # Position de départ pour centrer la grille - Boutons plus haut
    start_x = (screen_rect.width - total_width) // 2
    start_y = 160  # Remonté pour laisser plus de place en bas
    
    # Création des boutons de type de jeu (première ligne)
    game_buttons = []
    for col in range(3):
        x = start_x + col * (button_width + horizontal_spacing)
        y = start_y
        rect = pygame.Rect(x, y, button_width, button_height)
        game_buttons.append(rect)
    
    # Création des boutons d'adversaire (deuxième ligne)
    opponent_buttons = []
    for col in range(3):
        x = start_x + col * (button_width + horizontal_spacing)
        y = start_y + button_height + vertical_spacing
        rect = pygame.Rect(x, y, button_width, button_height)
        opponent_buttons.append(rect)
    
    # Bouton Retour - Repositionné plus haut
    back_button_width = 160  # Légèrement réduit
    back_button_height = 50  # Réduit pour être plus en harmonie
    back_button = pygame.Rect(
        (screen_rect.width - back_button_width) // 2,
        start_y + (button_height + vertical_spacing) * 2 + 30,  # Position ajustée
        back_button_width, back_button_height
    )
    
    # Vérifier que le bouton Retour est bien dans la fenêtre
    if back_button.bottom > screen_rect.height - 20:  # Garder une marge de 20px
        # Ajuster la position si nécessaire
        back_button.bottom = screen_rect.height - 20
    
    def draw_centered_text(text, rect, color):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        mode_screen.blit(text_surf, text_rect)
    
    def draw_section_title(text, x, y):
        title_surf = title_font.render(text, True, BLACK)
        title_rect = title_surf.get_rect(center=(x, y))
        mode_screen.blit(title_surf, title_rect)
    
    running = True
    while running:
        mode_screen.fill(WHITE)
        
        # Afficher les titres des sections
        draw_section_title("Choisissez votre jeu", screen_rect.width // 2, start_y - 40)
        draw_section_title("Choisissez votre adversaire", screen_rect.width // 2, start_y + button_height + vertical_spacing - 40)
        
        # Dessiner les boutons de type de jeu avec le bouton sélectionné en rouge
        for i, rect in enumerate(game_buttons):
            color = RED if i == selected_game else BLUE
            pygame.draw.rect(mode_screen, color, rect)
            draw_centered_text(game_types[i], rect, WHITE)
        
        # Dessiner les boutons d'adversaire avec le bouton sélectionné en rouge
        for i, rect in enumerate(opponent_buttons):
            color = RED if i == selected_opponent else BLUE
            pygame.draw.rect(mode_screen, color, rect)
            draw_centered_text(opponent_types[i], rect, WHITE)
        
        # Dessiner le bouton Retour
        pygame.draw.rect(mode_screen, BLUE, back_button)
        draw_centered_text("Retour", back_button, WHITE)
        
        # Si c'est la première exécution, afficher un message spécial
        if FIRST_RUN:
            first_run_text = "Mode par défaut sélectionné"
            info_text = font.render(first_run_text, True, BLACK)
            info_rect = info_text.get_rect(center=(screen_rect.width // 2, 80))
            mode_screen.blit(info_text, info_rect)
        
        # Afficher la sélection actuelle
        current_selection = f"Mode actuel : {game_types[selected_game]} - {opponent_types[selected_opponent]}"
        selection_text = font.render(current_selection, True, BLACK)
        selection_rect = selection_text.get_rect(center=(screen_rect.width // 2, back_button.top - 30))
        mode_screen.blit(selection_text, selection_rect)
        
        # Centrer la fenêtre de mode dans l'écran principal
        screen_main_rect = screen.get_rect()
        mode_pos = ((screen_main_rect.width - screen_rect.width) // 2, 
                    (screen_main_rect.height - screen_rect.height) // 2)
        
        # Afficher la fenêtre de mode sur l'écran principal
        screen.fill(WHITE)
        screen.blit(mode_screen, mode_pos)
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Ajuster les coordonnées de la souris pour correspondre à notre fenêtre de mode
                mouse_pos = (event.pos[0] - mode_pos[0], event.pos[1] - mode_pos[1])
                
                # Vérifier si un bouton de type de jeu a été cliqué
                for i, rect in enumerate(game_buttons):
                    if rect.collidepoint(mouse_pos):
                        selected_game = i
                        GLOBAL_SELECTED_GAME = i  # Mettre à jour la variable globale
                        FIRST_RUN = False  # Ce n'est plus le premier lancement
                
                # Vérifier si un bouton d'adversaire a été cliqué
                for i, rect in enumerate(opponent_buttons):
                    if rect.collidepoint(mouse_pos):
                        selected_opponent = i
                        GLOBAL_SELECTED_OPPONENT = i  # Mettre à jour la variable globale
                        FIRST_RUN = False  # Ce n'est plus le premier lancement
                
                # Vérifier si le bouton Retour a été cliqué
                if back_button.collidepoint(mouse_pos):
                    # Enregistrer les préférences de jeu ici si nécessaire
                    print(f"Mode sélectionné: {game_types[selected_game]} - {opponent_types[selected_opponent]}")
                    running = False
        
        pygame.display.flip()