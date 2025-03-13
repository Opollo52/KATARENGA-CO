import pygame
from menu import run_menu

taille = [500, 500]
if __name__ == "__main__":
    # Configuration de base
    pygame.init()
    screen = pygame.display.set_mode((taille[0], taille[1]))
    pygame.display.set_caption("Jeu Pygame")
    
    
    # Lancement du menu principal
    run_menu(screen)
    pygame.quit()