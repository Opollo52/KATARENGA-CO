import pygame

def run_menu(screen):
    # Définition des couleurs
    WHITE = (255, 255, 255)
    BLUE = (50, 100, 200)  # Harmonisé avec game_modes
    RED = (255, 50, 50)    # Harmonisé avec game_modes
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
        screen.fill(WHITE)
        
        # Dessin des boutons avec style harmonisé
        pygame.draw.rect(screen, BLUE, button_start)
        pygame.draw.rect(screen, RED, button_quit)
        
        # Bordure légèrement plus claire pour un effet d'arrondi visuel
        pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in BLUE), button_start, 2)
        pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in RED), button_quit, 2)
        
        # Textes des boutons
        draw_centered_text("Start", button_start, WHITE)
        draw_centered_text("Quitter", button_quit, WHITE)

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_start.collidepoint(event.pos):
                    # Importer ici pour éviter l'importation circulaire
                    from settings import show_settings
                    show_settings(screen)
                if button_quit.collidepoint(event.pos):
                    running = False

        pygame.display.flip()