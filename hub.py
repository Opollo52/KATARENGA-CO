import pygame
import os
import sys
from quadrant import show_quadrant
from game_modes import show_game_modes

def show_settings(screen):
    # Définition des couleurs
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    background_image = pygame.image.load(os.path.join(script_dir, "img", "fond.png"))
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (176, 242, 194)   
    BLUE = (169, 203, 215)   
    RED = (255, 105, 97)      
    font = pygame.font.Font(None, 36)

    # Configuration dynamique des boutons
    screen_rect = screen.get_rect()
    texts = ["Jouer", "Quadrant", "Paramètres", "Quitter"]
    max_width = max(font.render(text, True, WHITE).get_width() for text in texts)
    button_width = max_width + 40
    button_height = 50
    spacing = 20

    # Calcul des positions
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
                    show_game_modes(screen)  # Utilise directement show_game_modes avec le bouton Jouer
                elif buttons[1].collidepoint(event.pos):  # Quadrant
                    show_quadrant(screen)
                elif buttons[2].collidepoint(event.pos):  # Paramètres
                    show_settings(screen)
                elif buttons[3].collidepoint(event.pos):  # Quitter
                    running = False

        pygame.display.flip()