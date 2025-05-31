import pygame
import sys
from pathlib import Path
from assets.colors import Colors
from save import save_game

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

from save.save_game import save_manager
from plateau import game_setup
from menus.hub import show_settings

def prompt_new_or_load(screen):
    import pygame
    font = pygame.font.Font(None, 48)
    running = True
    while running:
        screen.fill((30, 30, 30))
        title = font.render("Choisir une option", True, (255, 255, 255))
        screen.blit(title, (100, 50))

        new_game_btn = font.render("1 - Nouvelle Partie", True, (0, 255, 0))
        load_game_btn = font.render("2 - Charger une Partie", True, (0, 200, 255))
        screen.blit(new_game_btn, (100, 150))
        screen.blit(load_game_btn, (100, 220))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_setup.show_game_setup(screen)
                    show_settings(screen)
                    running = False
                elif event.key == pygame.K_2:
                    save_data = save_manager.load_game()
                    if save_data:
                        from plateau.game_board import resume_game_from_save
                        resume_game_from_save(screen, save_data)
                    else:
                        print("Aucune sauvegarde trouvée.")

                

def run_menu(screen):
    # Définition des couleurs
    script_dir = Path(sys.argv[0]).parent.absolute()
    background_image = pygame.image.load(script_dir / "assets" / "img" / "fond.png")
    logo_image = pygame.image.load(script_dir / "assets" / "img" / "logo.png")
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
            if buttons[0].collidepoint(event.pos):
                prompt_new_or_load(screen)
                return

                if buttons[0].collidepoint(event.pos):  # Start
                    # Importer ici pour éviter l'importation circulaire
                    from menus.hub import show_settings
                    show_settings(screen)
                elif buttons[1].collidepoint(event.pos):  # Quitter
                    running = False

        pygame.display.flip()