import pygame
import os
import sys
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
def run_menu(screen):
    # Définition des couleurs
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    background_image = pygame.image.load(os.path.join(script_dir, "img", "fond.png"))
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE = (169, 203, 215)  # 
    RED = (255, 105, 97)    
    font = pygame.font.Font(None, 36)

    # Configuration dynamique des boutons
    screen_rect = screen.get_rect()
    texts = ["Start", "Quitter"]
    max_width = max(font.render(text, True, WHITE).get_width() for text in texts)
    button_width = max_width + 40
    button_height = 50
    spacing = 20

    # Calcul des positions
    total_height = (button_height * 2) + spacing
    start_y = (screen_rect.height - total_height) // 2

    # Création des boutons
    button_start = pygame.Rect((screen_rect.width - button_width)//2, start_y, button_width, button_height)
    button_quit = pygame.Rect((screen_rect.width - button_width)//2, start_y + button_height + spacing, button_width, button_height)

    def draw_centered_text(text, rect, color):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    running = True
    while running:
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))
        
        # Dessin des boutons avec style harmonisé
        pygame.draw.rect(screen, BLUE, button_start)
        pygame.draw.rect(screen, RED, button_quit)
        
        # Bordure légèrement plus claire pour un effet d'arrondi visuel
        pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in BLUE), button_start, 2)
        pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in RED), button_quit, 2)
        
        # Textes des boutons
        draw_centered_text("Start", button_start, BLACK)
        draw_centered_text("Quitter", button_quit, BLACK)

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_start.collidepoint(event.pos):
                    # Importer ici pour éviter l'importation circulaire
                    from hub import show_settings
                    show_settings(screen)
                if button_quit.collidepoint(event.pos):
                    running = False

        pygame.display.flip()