import pygame
from menus.menu import run_menu
from config_manager import initialize_quadrants
from jeux.isolation import run_isolation

if __name__ == "__main__":
    # Initialiser les quadrants et récupérer la configuration
    config, _ = initialize_quadrants()
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    pygame.display.set_caption("Jeu Pygame")

    # Lancement du menu principal
    selected_game = run_menu(screen)  # ✅ Doit retourner un identifiant de mode

    # Redirection selon le mode de jeu choisi
    if selected_game == "Isolation":
        run_isolation(screen)

    pygame.quit()