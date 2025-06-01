import pygame
import sys
from pathlib import Path
from assets.colors import Colors
from assets.audio_manager import audio_manager  # IMPORT AUDIO

# Variables globales pour garder le mode de jeu et l'adversaire
GLOBAL_SELECTED_GAME = 0 
GLOBAL_SELECTED_OPPONENT = 0
FIRST_RUN = True

def reset_game_state():
    """BUG FIX 1: Fonction pour réinitialiser l'état du jeu"""
    global GLOBAL_SELECTED_GAME, GLOBAL_SELECTED_OPPONENT
    # Cette fonction sera appelée quand on revient au menu
    pass  # Les variables gardent leur valeur pour permettre la sélection

def show_game_modes(screen):
    """
    Affiche la fenêtre de sélection des modes de jeu.
    """
    global GLOBAL_SELECTED_GAME, GLOBAL_SELECTED_OPPONENT, FIRST_RUN
    
    # BUG FIX 1: Réinitialiser les variables de jeu au retour
    reset_game_state()
    
    # Utiliser les dimensions actuelles de l'écran pour un meilleur centrage
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    pygame.display.set_caption("Sélection du mode de jeu")
    #couleurs
    script_dir = Path(__file__).parent.parent.absolute()
    background_image = pygame.image.load(script_dir / "assets" / "img" / "fond.png")
    BLACK = Colors.BLACK
    GREEN = Colors.GREEN 
    BLUE = Colors.BLUE   
    RED = Colors.RED      
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 42)
    
    # Configuration de l'écran
    screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
    
    # Options disponibles
    game_types = ["Katarenga", "Congress", "Isolation"]
    opponent_types = ["Ordi", "Local", "Réseau"]
    
    # BUG FIX 1: Utiliser des variables locales pour éviter les conflits
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
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))
        
        # Afficher les titres des sections
        title_text = title_font.render("Choisissez votre jeu", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, game_title_y))

        # Créer une surface transparente
        bg_surface = pygame.Surface((title_rect.width + 16, title_rect.height + 8), pygame.SRCALPHA)
        bg_surface.fill((255, 255, 255, 120))
        screen.blit(bg_surface, (title_rect.x - 8, title_rect.y - 4))

        screen.blit(title_text, title_rect)  
        # Titre de la section adversaire      
        opponent_title_text = title_font.render("Choisissez votre adversaire", True, BLACK)
        opponent_title_rect = opponent_title_text.get_rect(center=(WIDTH // 2, opponent_title_y))

        bg_surface = pygame.Surface((opponent_title_rect.width + 16, opponent_title_rect.height + 8), pygame.SRCALPHA)
        bg_surface.fill((255, 255, 255, 120))
        screen.blit(bg_surface, (opponent_title_rect.x - 8, opponent_title_rect.y - 4))

        screen.blit(opponent_title_text, opponent_title_rect)

        # Dessiner les boutons de type de jeu avec le bouton sélectionné en rouge
        for i, rect in enumerate(game_buttons):
            color = RED if i == selected_game else BLUE
            pygame.draw.rect(screen, color, rect)
            draw_centered_text(game_types[i], rect, BLACK)
        
        # Dessiner les boutons d'adversaire avec le bouton sélectionné en rouge
        for i, rect in enumerate(opponent_buttons):
            color = RED if i == selected_opponent else BLUE
            pygame.draw.rect(screen, color, rect)
            draw_centered_text(opponent_types[i], rect, BLACK)
        
        # Dessiner le bouton Jouer
        pygame.draw.rect(screen, GREEN, play_button)
        draw_centered_text("Jouer", play_button, BLACK)
        
        # Dessiner le bouton Retour
        pygame.draw.rect(screen, BLUE, back_button)
        draw_centered_text("Retour", back_button, BLACK)
        
        # Si c'est la première exécution, afficher un message spécial
        if FIRST_RUN:
            first_text = font.render("Mode par défaut sélectionné", True, BLACK)
            first_rect = first_text.get_rect(center=(WIDTH // 2, start_y - 30))
            
            bg_surface = pygame.Surface((first_rect.width + 16, first_rect.height + 8), pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 120))
            screen.blit(bg_surface, (first_rect.x - 8, first_rect.y - 4))
            
            screen.blit(first_text, first_rect)
        
        # Afficher la sélection actuelle
        current_selection = f"Mode actuel : {game_types[selected_game]} - {opponent_types[selected_opponent]}"
        selection_text = font.render(current_selection, True, BLACK)
        selection_rect = selection_text.get_rect(center=(WIDTH // 2, selection_text_y))

        bg_surface = pygame.Surface((selection_rect.width + 16, selection_rect.height + 8), pygame.SRCALPHA)
        bg_surface.fill((255, 255, 255, 120))
        screen.blit(bg_surface, (selection_rect.x - 8, selection_rect.y - 4))

        screen.blit(selection_text, selection_rect)
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier si un bouton de type de jeu a été cliqué
                for i, rect in enumerate(game_buttons):
                    if rect.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')  #   gestion SON
                        selected_game = i
                        GLOBAL_SELECTED_GAME = i  # BUG FIX 1: Mise à jour immédiate
                        FIRST_RUN = False
                
                # Vérifier si un bouton d'adversaire a été cliqué
                for i, rect in enumerate(opponent_buttons):
                    if rect.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')  #  gestion SON
                        selected_opponent = i
                        GLOBAL_SELECTED_OPPONENT = i  # BUG FIX 1: Mise à jour immédiate
                        FIRST_RUN = False
                
                # Vérifier si le bouton Jouer a été cliqué
                if play_button.collidepoint(event.pos):
                    audio_manager.play_sound('button_click')  #   gestion SON
                    # BUG FIX 1: S'assurer que les variables globales sont à jour
                    GLOBAL_SELECTED_GAME = selected_game
                    GLOBAL_SELECTED_OPPONENT = selected_opponent
                    
                    print(f"Lancement du jeu: Mode {game_types[selected_game]} - Adversaire {opponent_types[selected_opponent]}")
                    
                    if selected_opponent == 2:  # Réseau
                        try:
                            from résseaux.network_menu import show_network_menu
                            running = False
                            show_network_menu(screen)
                        except ImportError as e:
                            print(f"Erreur d'import network_menu: {e}")
                            # Fallback vers le jeu normal si le module réseau n'est pas disponible
                            from plateau.game_setup import show_game_setup
                            running = False
                            show_game_setup(screen)
                    else:
                        # Lancer la configuration de la partie normale
                        from plateau.game_setup import show_game_setup
                        running = False
                        show_game_setup(screen)
                
                # Vérifier si le bouton Retour a été cliqué
                if back_button.collidepoint(event.pos):
                    audio_manager.play_sound('button_click')  #   gestion SON
                    print(f"Mode sélectionné: {game_types[selected_game]} - {opponent_types[selected_opponent]}")
                    running = False
        
        pygame.display.flip()
