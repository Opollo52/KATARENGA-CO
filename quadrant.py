import pygame

def show_quadrant(screen):
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    font = pygame.font.Font(None, 36)

    # Définition des boutons
    screen_rect = screen.get_rect()
    texts = ["Voir les quadrants", "Créer un quadrant", "Retour"]
    max_width = max(font.render(text, True, WHITE).get_width() for text in texts)
    button_width = max_width + 40
    button_height = 50
    spacing = 20

    total_height = (button_height * 3) + (spacing * 2)
    start_y = (screen_rect.height - total_height) // 2

    buttons = [
        pygame.Rect(
            (screen_rect.width - button_width) // 2,
            start_y + i * (button_height + spacing),
            button_width,
            button_height
        ) for i in range(3)
    ]

    def draw_centered_text(text, rect, color):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    running = True
    while running:
        screen.fill(WHITE)

        colors = [BLUE, RED, BLUE]
        for rect, color in zip(buttons, colors):
            pygame.draw.rect(screen, color, rect)

        for text, rect in zip(texts, buttons):
            draw_centered_text(text, rect, WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].collidepoint(event.pos):  # Voir quadrants
                    print("Affichage des quadrants sauvegardés (à implémenter)")
                elif buttons[1].collidepoint(event.pos):  # Créer un quadrant
                    from creator import run_creator  # Importation à la volée pour éviter l'import circulaire
                    run_creator(screen)  # Appel de la fonction pour lancer le créateur
                elif buttons[2].collidepoint(event.pos):  # Quitter
                    running = False

        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((600, 500))
    pygame.display.set_caption("Menu des Quadrants")
    show_quadrant(screen)
    pygame.quit()
