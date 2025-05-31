import pygame
import sys
from pathlib import Path
from assets.colors import Colors

def show_quadrant(screen):
    # Récupérer les dimensions de l'écran
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    #couleurs
    script_dir = Path(__file__).parent.parent.absolute()
    background_image = pygame.image.load(script_dir / "assets" / "img" / "fond.png")
    
    WHITE = Colors.WHITE
    BLACK = Colors.BLACK
    BLUE = Colors.BLUE 
    RED = Colors.RED 
    GREEN = Colors.GREEN   
    
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 42)  

    # Définition des boutons
    screen_rect = screen.get_rect()
    texts = ["Voir les quadrants", "Créer un quadrant", "Retour"]
    max_width = max(font.render(text, True, WHITE).get_width() for text in texts)
    button_width = max_width + 40
    button_height = 50
    spacing = 20

    total_height = (button_height * 3) + (spacing * 2)
    # Centrage vertical
    start_y = (HEIGHT - total_height) // 2

    buttons = [
        pygame.Rect(
            (WIDTH - button_width) // 2,  # Centrage horizontal
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
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))
        
        # Titre centré au-dessus des boutons
        title = title_font.render("Menu des Quadrants", True, BLACK)
        title_rect = title.get_rect(center=(WIDTH//2, start_y - 40))
        
        # Fond blanc semi-transparent derrière le titre
        title_bg_rect = title_rect.inflate(16, 8)
        title_bg_surface = pygame.Surface((title_bg_rect.width, title_bg_rect.height), pygame.SRCALPHA)
        title_bg_surface.fill((*WHITE, 200))  # Blanc de Colors.py avec transparence
        screen.blit(title_bg_surface, title_bg_rect)
        
        screen.blit(title, title_rect)

        # Alternance de couleurs BLUE et RED comme dans game_modes
        colors = [BLUE, GREEN, RED]
        for i, (rect, color) in enumerate(zip(buttons, colors)):
            pygame.draw.rect(screen, color, rect)
            # Ajouter un léger arrondi visuel avec une bordure plus claire
            pygame.draw.rect(screen, tuple(min(c + 30, 255) for c in color), rect, 2)

        for i, (text, rect) in enumerate(zip(texts, buttons)):
            draw_centered_text(text, rect, BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].collidepoint(event.pos):  # Voir quadrants
                    from quadrant.quadrant_viewer import show_quadrant_library
                    show_quadrant_library(screen)
                elif buttons[1].collidepoint(event.pos):  # Créer un quadrant
                    from quadrant.creator import run_creator  # Importation à la volée pour éviter l'import circulaire
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