import pygame
import sys
from pathlib import Path
from menus.menu_quadrant import show_quadrant
from plateau.game_modes import show_game_modes
from assets.colors import Colors
from assets.audio_manager import audio_manager 
from menus.settings_menu import show_settings_menu  

def show_settings(screen):
    # Définition des couleurs
    script_dir = Path(__file__).parent.parent.absolute()
    background_image = pygame.image.load(script_dir / "assets" / "img" / "fond.png")
    logo_image = pygame.image.load(script_dir / "assets" / "img" / "logo.png")
    WHITE = Colors.WHITE
    BLACK = Colors.BLACK
    GREEN = Colors.GREEN
    BLUE = Colors.BLUE
    RED = Colors.RED   
          
    font = pygame.font.Font(None, 36)

    # Configuration dynamique des boutons
    screen_rect = screen.get_rect()
    texts = ["Jouer", "Quadrant", "Paramètres", "Quitter"]
    max_width = max(font.render(text, True, WHITE).get_width() for text in texts)
    button_width = max_width + 40
    button_height = 50
    spacing = 20

    # Configuration du logo (centré verticalement comme les boutons)
    logo_height = 200  # Logo plus gros
    logo_ratio = logo_image.get_width() / logo_image.get_height()
    logo_width = int(logo_height * logo_ratio)
    logo_scaled = pygame.transform.scale(logo_image, (logo_width, logo_height))
    logo_y = (screen_rect.height - logo_height) // 7  # Centré verticalement
    logo_x = (screen_rect.width - logo_width) // 2

    # Calcul des positions des boutons (position d'origine)
    total_height = (button_height * len(texts)) + (spacing * (len(texts) - 1))
    start_y = (screen_rect.height - total_height) // 2

    # Création des boutons
    buttons = [
        pygame.Rect((screen_rect.width - button_width)//2, start_y + i * (button_height + spacing), button_width, button_height)
        for i in range(len(texts))
    ]

    def draw_centered_text(text, rect, color):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    running = True
    while running:
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))
        
        # Affichage du logo
        screen.blit(logo_scaled, (logo_x, logo_y))
        
        # Dessin des boutons avec style harmonisé - Utilisation des couleurs bleue et rouge uniquement
        colors = [BLUE, GREEN, GREEN, RED]  
        
        for i, (rect, color) in enumerate(zip(buttons, colors)):
            pygame.draw.rect(screen, color, rect)
            # Bordure légèrement plus claire pour un effet d'arrondi visuel
            pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in color), rect, 2)
            
            # Textes des boutons
            draw_centered_text(texts[i], rect, BLACK)

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].collidepoint(event.pos):  # Jouer
                    audio_manager.play_sound('button_click')  #  gestion SON
                    show_game_modes(screen)  # Utilise directement show_game_modes avec le bouton Jouer
                elif buttons[1].collidepoint(event.pos):  # Quadrant
                    audio_manager.play_sound('button_click')  #   gestion SON
                    show_quadrant(screen)
                elif buttons[2].collidepoint(event.pos):  # Paramètres
                    audio_manager.play_sound('button_click')  #  gestion SON
                    show_settings_menu(screen)  #   PAGE SETTINGS
                elif buttons[3].collidepoint(event.pos):  # Quitter
                    audio_manager.play_sound('button_click')  #   gestion SON
                    running = False

        pygame.display.flip()
