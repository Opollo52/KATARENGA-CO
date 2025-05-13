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
    Fenêtre de 800x600 pixels (agrandie)
    """
    global GLOBAL_SELECTED_GAME, GLOBAL_SELECTED_OPPONENT, FIRST_RUN
    
    # Sauvegarder la taille originale
    original_size = screen.get_size()
    
    # Créer une nouvelle surface agrandie de 800x600 pixels (au lieu de 600x600)
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sélection du mode de jeu")
    
    WHITE = (255, 255, 255)
    BLUE = (50, 100, 200)  # Couleur par défaut des boutons
    RED = (255, 50, 50)    # Couleur des boutons sélectionnés
    BLACK = (0, 0, 0)
    GREEN = (50, 180, 50)  # Couleur pour le bouton Jouer
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
    
    # Bouton Jouer et Retour sur la même ligne
    button_row_y = start_y + (button_height + vertical_spacing) * 2 + 20  # Ajout d'un peu plus d'espace
    
    # Bouton Jouer - Repositionné à gauche
    play_button_width = 180
    play_button_height = 60
    play_button = pygame.Rect(
        (screen_rect.width // 2) - play_button_width - 20,  # Décalé à gauche
        button_row_y,
        play_button_width, 
        play_button_height
    )
    
    # Bouton Retour - Repositionné à droite
    back_button_width = 180
    back_button_height = 60
    back_button = pygame.Rect(
        (screen_rect.width // 2) + 20,  # Décalé à droite
        button_row_y,
        back_button_width, 
        back_button_height
    )
    
    def draw_centered_text(text, rect, color):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
    
    def draw_section_title(text, x, y):
        title_surf = title_font.render(text, True, BLACK)
        title_rect = title_surf.get_rect(center=(x, y))
        screen.blit(title_surf, title_rect)
    
    running = True
    while running:
        screen.fill(WHITE)
        
        # Afficher les titres des sections
        draw_section_title("Choisissez votre jeu", screen_rect.width // 2, start_y - 40)
        draw_section_title("Choisissez votre adversaire", screen_rect.width // 2, start_y + button_height + vertical_spacing - 40)
        
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
            info_rect = info_text.get_rect(center=(screen_rect.width // 2, 80))
            screen.blit(info_text, info_rect)
        
        # Afficher la sélection actuelle
        current_selection = f"Mode actuel : {game_types[selected_game]} - {opponent_types[selected_opponent]}"
        selection_text = font.render(current_selection, True, BLACK)
        selection_rect = selection_text.get_rect(center=(screen_rect.width // 2, play_button.top - 30))
        screen.blit(selection_text, selection_rect)
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.set_mode(original_size)  # Restaurer la taille d'origine
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
                    # Restaurer la taille d'écran originale avant de passer à l'écran suivant
                    pygame.display.set_mode(original_size)
                    running = False
                    show_game_setup(screen)
                
                # Vérifier si le bouton Retour a été cliqué
                if back_button.collidepoint(event.pos):
                    # Enregistrer les préférences de jeu ici si nécessaire
                    print(f"Mode sélectionné: {game_types[selected_game]} - {opponent_types[selected_opponent]}")
                    # Restaurer la taille d'écran originale avant de revenir
                    pygame.display.set_mode(original_size)
                    running = False
        
        pygame.display.flip() 