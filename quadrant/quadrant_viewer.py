# quadrant_viewer.py modifié
import pygame
import sys
from pathlib import Path
from config_manager import initialize_quadrants
from assets.colors import Colors

def load_quadrants():
    """Charge les quadrants depuis le fichier JSON en initialisant si nécessaire"""
    # Utiliser le gestionnaire de configuration pour initialiser les quadrants
    _, quadrants_data = initialize_quadrants()
    return quadrants_data

def show_quadrant_library(screen):
    """Affiche la bibliothèque de quadrants avec une interface épurée"""
    # Obtenir les dimensions actuelles de l'écran
    screen_rect = screen.get_rect()
    WIDTH, HEIGHT = screen_rect.width, screen_rect.height
    
    pygame.display.set_caption("Bibliothèque de Quadrants")
    
    # Couleurs
    script_dir = Path(sys.argv[0]).parent.absolute()
    background_image = pygame.image.load(script_dir / "assets" / "img" / "fond.png")
    WHITE = Colors.WHITE
    BLACK = Colors.BLACK
    LIGHT_GRAY = Colors.LIGHT_GRAY
    DARK_GRAY = Colors.DARK_GRAY
    RED = Colors.RED
    # Polices - tailles adaptatives
    title_font = pygame.font.Font(None, int(HEIGHT * 0.06))  # 6% de la hauteur
    button_font = pygame.font.Font(None, int(HEIGHT * 0.04))  # 4% de la hauteur
    
    # Chargement des quadrants
    quadrants = load_quadrants()
    
    # Préchargement des images
    quadrant_images = {}
    quadrant_rects = {}
    
    for quadrant_id, data in quadrants.items():
        image_path = data.get("image_path")
        if image_path and Path(image_path).exists():
            try:
                img = pygame.image.load(image_path)
                quadrant_images[quadrant_id] = img
            except pygame.error:
                print(f"Erreur lors du chargement de l'image pour {quadrant_id}")
    
    # État de l'interface
    view_mode = "library"  # "library" ou "detail"
    selected_quadrant = None
    
    # Bouton retour harmonisé avec le style des autres pages - dimensions adaptatives
    button_width = WIDTH * 0.15  # 15% de la largeur
    button_height = HEIGHT * 0.08  # 8% de la hauteur
    back_button = pygame.Rect(WIDTH * 0.05, HEIGHT - HEIGHT * 0.12, button_width, button_height)
    
    # Variables pour le défilement de la bibliothèque
    scroll_y = 0
    scroll_speed = int(HEIGHT * 0.05)  # 5% de la hauteur
    max_scroll = 0  # Sera calculé dynamiquement
    
    # Boutons de défilement
    scroll_button_size = int(HEIGHT * 0.05)  # 5% de la hauteur
    scroll_up_button = pygame.Rect(WIDTH - WIDTH * 0.1, HEIGHT * 0.15, scroll_button_size, scroll_button_size)
    scroll_down_button = pygame.Rect(WIDTH - WIDTH * 0.1, HEIGHT - HEIGHT * 0.15, scroll_button_size, scroll_button_size)
    
    # Génération d'une grille d'emplacements pour les quadrants avec défilement
    def generate_grid(scroll_position):
        thumbnail_size = min(WIDTH * 0.18, HEIGHT * 0.25)  # Taille adaptative 
        padding = int(WIDTH * 0.02)  # 2% de la largeur
        columns = max(1, (WIDTH - padding * 2 - WIDTH * 0.1) // (thumbnail_size + padding))
        
        grid_rects = {}
        col, row = 0, 0
        
        for quadrant_id in quadrants:
            x = padding + col * (thumbnail_size + padding)
            y = padding + row * (thumbnail_size + padding) + HEIGHT * 0.1 - scroll_position
            
            rect = pygame.Rect(x, y, thumbnail_size, thumbnail_size)
            grid_rects[quadrant_id] = rect
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
        
        # Calculer la hauteur totale du contenu
        if len(quadrants) > 0:
            num_rows = (len(quadrants) + columns - 1) // columns
            total_height = num_rows * (thumbnail_size + padding) + padding + HEIGHT * 0.1
            return grid_rects, total_height
        else:
            return grid_rects, 0
    
    def draw_centered_text(text, rect, color):
        """Dessine un texte centré dans un rectangle"""
        text_surf = button_font.render(text, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
    
    running = True
    while running:
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))
        
        # Calculer la grille en tenant compte du défilement
        quadrant_rects, total_content_height = generate_grid(scroll_y)
        max_scroll = max(0, total_content_height - (HEIGHT - HEIGHT * 0.2))  # Espace en haut et en bas
        
        # Mode bibliothèque - affichage de tous les quadrants en grille
        if view_mode == "library":
            # Titre discret
            title = title_font.render("Bibliothèque de Quadrants", True, BLACK)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT * 0.05))
            
            if not quadrants:
                no_quadrants = title_font.render("Aucun quadrant disponible", True, DARK_GRAY)
                screen.blit(no_quadrants, (WIDTH//2 - no_quadrants.get_width()//2, HEIGHT//2))
            else:
                # Zone de clipping pour la bibliothèque
                library_area = pygame.Rect(0, HEIGHT * 0.1, WIDTH, HEIGHT - HEIGHT * 0.2)
                
                # Créer une surface pour dessiner les quadrants
                library_surface = pygame.Surface((WIDTH, total_content_height), pygame.SRCALPHA)
                library_surface.fill((0, 0, 0, 0))  # Transparent
                
                # Affichage des miniatures en grille
                for quadrant_id, rect in quadrant_rects.items():
                    # Calculer la position relative à la surface de la bibliothèque
                    rel_rect = pygame.Rect(rect.x, rect.y + scroll_y - HEIGHT * 0.1, rect.width, rect.height)
                    
                    # Fond gris clair pour chaque emplacement
                    pygame.draw.rect(library_surface, LIGHT_GRAY, rel_rect)
                    pygame.draw.rect(library_surface, DARK_GRAY, rel_rect, 2)
                    
                    if quadrant_id in quadrant_images:
                        # Redimensionner l'image pour qu'elle s'adapte à l'emplacement
                        img = quadrant_images[quadrant_id]
                        thumbnail = pygame.transform.scale(img, (rect.width - 10, rect.height - 10))
                        
                        # Centrer l'image dans son emplacement
                        img_rect = thumbnail.get_rect(center=rel_rect.center)
                        library_surface.blit(thumbnail, img_rect.topleft)
                        
                        # Petit numéro discret en bas à droite
                        q_num = quadrant_id.split('_')[1]
                        num_font = pygame.font.Font(None, int(HEIGHT * 0.03))  # Taille adaptative
                        num_text = num_font.render(q_num, True, BLACK)
                        library_surface.blit(num_text, (rel_rect.right - num_text.get_width() - 5, 
                                                      rel_rect.bottom - num_text.get_height() - 5))
                
                # Afficher la surface de la bibliothèque avec clipping
                screen.blit(library_surface, (0, HEIGHT * 0.1), area=pygame.Rect(0, scroll_y, WIDTH, library_area.height))
                
                # Dessiner les boutons de défilement
                if max_scroll > 0:
                    # Dessiner le bouton haut
                    pygame.draw.rect(screen, DARK_GRAY, scroll_up_button)
                    pygame.draw.polygon(screen, WHITE, [
                        (scroll_up_button.centerx, scroll_up_button.top + 5),
                        (scroll_up_button.left + 5, scroll_up_button.bottom - 5),
                        (scroll_up_button.right - 5, scroll_up_button.bottom - 5)
                    ])
                    
                    # Dessiner le bouton bas
                    pygame.draw.rect(screen, DARK_GRAY, scroll_down_button)
                    pygame.draw.polygon(screen, WHITE, [
                        (scroll_down_button.centerx, scroll_down_button.bottom - 5),
                        (scroll_down_button.left + 5, scroll_down_button.top + 5),
                        (scroll_down_button.right - 5, scroll_down_button.top + 5)
                    ])
        
        # Mode détail - affichage d'un seul quadrant
        else:
            if selected_quadrant in quadrant_images:
                # Afficher l'image du quadrant à sa taille maximale tout en conservant les proportions
                img = quadrant_images[selected_quadrant]
                img_width, img_height = img.get_size()
                
                # Calculer la taille adaptée à l'écran
                display_area_width = WIDTH * 0.8  # 80% de la largeur
                display_area_height = HEIGHT * 0.7  # 70% de la hauteur
                
                # Calculer le ratio pour conserver les proportions
                width_ratio = display_area_width / img_width
                height_ratio = display_area_height / img_height
                scale_ratio = min(width_ratio, height_ratio)
                
                # Nouvelles dimensions
                new_width = int(img_width * scale_ratio)
                new_height = int(img_height * scale_ratio)
                
                # Position centrée
                img_x = (WIDTH - new_width) // 2
                img_y = (HEIGHT - new_height) // 2
                
                # Redimensionner et afficher
                scaled_img = pygame.transform.scale(img, (new_width, new_height))
                screen.blit(scaled_img, (img_x, img_y))
                
                # Cadre léger autour de l'image
                pygame.draw.rect(screen, DARK_GRAY, (img_x, img_y, new_width, new_height), 2)
            
            # Dessiner un bouton retour discret (flèche)
            detail_back_button = pygame.Rect(WIDTH * 0.05, HEIGHT * 0.05, int(HEIGHT * 0.08), int(HEIGHT * 0.08))
            pygame.draw.circle(screen, LIGHT_GRAY, detail_back_button.center, detail_back_button.width // 2)
            pygame.draw.circle(screen, DARK_GRAY, detail_back_button.center, detail_back_button.width // 2, 2)
            
            # Dessiner une flèche vers la gauche
            arrow_points = [
                (detail_back_button.centerx - detail_back_button.width // 4, detail_back_button.centery),
                (detail_back_button.centerx + detail_back_button.width // 4, detail_back_button.centery - detail_back_button.height // 4),
                (detail_back_button.centerx + detail_back_button.width // 4, detail_back_button.centery + detail_back_button.height // 4)
            ]
            pygame.draw.polygon(screen, DARK_GRAY, arrow_points)
        
        # Bouton retour (harmonisé avec les autres)
        pygame.draw.rect(screen, RED, back_button)
        draw_centered_text("Retour", back_button, BLACK)
        
        # Traitement des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if view_mode == "library":
                    # Gestion du défilement
                    if event.button == 4:  # Molette vers le haut
                        scroll_y = max(0, scroll_y - scroll_speed)
                    elif event.button == 5:  # Molette vers le bas
                        scroll_y = min(max_scroll, scroll_y + scroll_speed)
                    
                    # Clic sur les boutons de défilement
                    if event.button == 1:  # Clic gauche
                        if scroll_up_button.collidepoint(event.pos):
                            scroll_y = max(0, scroll_y - scroll_speed)
                        elif scroll_down_button.collidepoint(event.pos):
                            scroll_y = min(max_scroll, scroll_y + scroll_speed)
                        
                        # Vérifier si un quadrant a été cliqué
                        for quadrant_id, rect in quadrant_rects.items():
                            # Limiter la zone de clic à la hauteur visible
                            visible_top = HEIGHT * 0.1
                            visible_bottom = HEIGHT - HEIGHT * 0.1
                            
                            if (rect.collidepoint(event.pos) and 
                                rect.top >= visible_top - rect.height and 
                                rect.bottom <= visible_bottom + rect.height):
                                
                                selected_quadrant = quadrant_id
                                view_mode = "detail"
                                break
                        
                        # Clic sur le bouton retour
                        if back_button.collidepoint(event.pos):
                            return
                else:
                    # En mode détail
                    if event.button == 1:  # Clic gauche
                        # Clic sur le bouton retour spécifique au mode détail
                        if detail_back_button.collidepoint(event.pos):
                            view_mode = "library"
                        # Clic sur le bouton retour principal (en bas)
                        elif back_button.collidepoint(event.pos):
                            return
                        # Tout autre clic (sauf sur les boutons) revient à la bibliothèque
                        elif not back_button.collidepoint(event.pos):
                            view_mode = "library"
            
        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Démarrer en plein écran
    show_quadrant_library(screen)
    pygame.quit()