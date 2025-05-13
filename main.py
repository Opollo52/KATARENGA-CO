import pygame
from menu import run_menu
from config_manager import initialize_quadrants

if __name__ == "__main__":
    # Initialiser les quadrants et récupérer la configuration
    config, _ = initialize_quadrants()
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    
    pygame.display.set_caption("Jeu Pygame")
    
    # Lancement du menu principal
    run_menu(screen)
    pygame.quit()