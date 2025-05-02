import pygame
from quadrant import show_quadrant
from game_modes import show_game_modes  # Import de notre nouvelle fonction

def show_settings(screen):
    WHITE = (255, 255, 255)
    BLUE = (50, 100, 200)  # Harmonisé avec game_modes
    RED = (255, 50, 50)    # Harmonisé avec game_modes
    font = pygame.font.Font(None, 36)

    # Configuration dynamique des boutons
    screen_rect = screen.get_rect()
    texts = ["Jouer", "Mode de jeu", "Créateur de quadrant", "Retour"]
    max_width = max(font.render(text, True, WHITE).get_width() for text in texts)
    button_width = max_width + 40
    button_height = 50
    spacing = 20

    # Calcul des positions
    total_height = (button_height * 4) + (spacing * 3)
    start_y = (screen_rect.height - total_height) // 2

    # Création des boutons
    buttons = [
        pygame.Rect((screen_rect.width - button_width) // 2, 
                    start_y + i * (button_height + spacing), 
                    button_width, button_height)
        for i in range(4)
    ]

    def draw_centered_text(text, rect, color):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    running = True
    while running:
        screen.fill(WHITE)
        
        # Dessin des boutons avec alternance BLUE et RED comme dans game_modes
        colors = [BLUE, RED, BLUE, RED]
        for rect, color in zip(buttons, colors):
            pygame.draw.rect(screen, color, rect)
            # Bordure légèrement plus claire pour un effet d'arrondi visuel
            pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in color), rect, 2)
        
        # Textes des boutons
        texts = ["Jouer", "Mode de jeu", "Créateur de quadrant", "Retour"]
        for text, rect in zip(texts, buttons):
            draw_centered_text(text, rect, WHITE)

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].collidepoint(event.pos):  # Jouer
                    from game_setup import show_game_setup
                    show_game_setup(screen)
                elif buttons[1].collidepoint(event.pos):  # Mode de jeu
                    show_game_modes(screen)  # Appel à notre nouvelle fonction
                elif buttons[2].collidepoint(event.pos):  # Créateur de quadrant
                    show_quadrant(screen)  # Lancer la gestion des quadrants
                elif buttons[3].collidepoint(event.pos):  # Bouton Retour
                    running = False

        pygame.display.flip()