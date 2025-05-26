import pygame
import os
import sys
from assets.colors import Colors

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
def run_menu(screen):
    # Définition des couleurs
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    background_image = pygame.image.load(os.path.join(script_dir, "assets", "img", "fond.png"))
    logo_image = pygame.image.load(os.path.join(script_dir, "assets", "img", "logo.png"))
    WHITE = Colors.WHITE
    BLACK = Colors.BLACK
    RED = Colors.RED
    BLUE = Colors.BLUE
    
    font = pygame.font.Font(None, 36)

    # Configuration dynamique des boutons (identique à hub.py)
    screen_rect = screen.get_rect()
    texts = ["Start", "Quitter"]
    max_width = max(font.render(text, True, WHITE).get_width() for text in texts)
    button_width = max_width + 40
    button_height = 50
    spacing = 20

    # Configuration du logo (identique à hub.py)
    logo_height = 200  # Logo plus gros
    logo_ratio = logo_image.get_width() / logo_image.get_height()
    logo_width = int(logo_height * logo_ratio)
    logo_scaled = pygame.transform.scale(logo_image, (logo_width, logo_height))
    logo_y = (screen_rect.height - logo_height) // 7  # Centré verticalement
    logo_x = (screen_rect.width - logo_width) // 2

    # Calcul des positions des boutons (identique à hub.py)
    total_height = (button_height * len(texts)) + (spacing * (len(texts) - 1))
    start_y = (screen_rect.height - total_height) // 2

    # Création des boutons (identique à hub.py)
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
        
        # Dessin des boutons avec style harmonisé (identique à hub.py)
        colors = [BLUE, RED]  
        
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
                if buttons[0].collidepoint(event.pos):  # Start
                    # Importer ici pour éviter l'importation circulaire
                    from hub import show_settings
                    show_settings(screen)
                elif buttons[1].collidepoint(event.pos):  # Quitter
                    running = False

        pygame.display.flip()