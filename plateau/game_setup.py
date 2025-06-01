import pygame
import json
import sys
from pathlib import Path
from quadrant.quadrant_viewer import load_quadrants
from assets.colors import Colors
from assets.audio_manager import audio_manager  # ✅ NOUVEAU IMPORT AUDIO

def show_game_setup(screen):
    """
    Interface pour configurer une partie en sélectionnant 4 quadrants
    """
    
    # Configuration
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    pygame.display.set_caption("Configuration de partie")
    
    # Couleurs
    script_dir = Path(__file__).parent.parent.absolute()
    background_image = pygame.image.load(script_dir / "assets" / "img" / "fond.png")
    WHITE = Colors.WHITE
    BLACK = Colors.BLACK    
    LIGHT_GRAY = Colors.LIGHT_GRAY
    DARK_GRAY = Colors.DARK_GRAY
    BLUE = Colors.BLUE  
    RED = Colors.RED    
    HIGHLIGHT = Colors.HIGHLIGHT
    
    # Polices
    title_font = pygame.font.Font(None, 36)
    button_font = pygame.font.Font(None, 30)
    instruction_font = pygame.font.Font(None, 16)
    
    # Fonction pour faire tourner une grille dans le sens horaire
    def rotate_grid(grid):
        """Tourne une grille 4x4 de 90 degrés dans le sens horaire"""
        rows = len(grid)
        cols = len(grid[0])
        rotated = [[0 for i in range(rows)] for j in range(cols)]
        
        for i in range(rows):
            for j in range(cols):
                rotated[j][rows - 1 - i] = grid[i][j]
        
        return rotated
    
    def apply_rotation_to_grid(grid, rotation):
        """
        Applique la rotation spécifiée (0, 90, 180, 270) à une grille
        """
        rotated_grid = [row.copy() for row in grid]  # Copie de la grille originale
        # Nombre de rotations de 90° à appliquer
        num_rotations = rotation // 90
        for i in range(num_rotations):
            rotated_grid = rotate_grid(rotated_grid)
        return rotated_grid
    
    def prepare_rotated_grids(quadrants_data):
        """
        Prépare toutes les orientations possibles pour chaque quadrant et les stocke dans le JSON.
        Si les orientations existent déjà, cette fonction ne fait rien.
        """
        need_save = False
        script_dir = Path(__file__).parent.parent.absolute()
        json_path = script_dir / "quadrant" / "quadrants.json"
        
        for quadrant_id, data in quadrants_data.items():
            # Vérifier si les orientations sont déjà préparées
            if "rotations" not in data:
                # S'assurer que nous avons une grille originale
                if "original_grid" not in data:
                    data["original_grid"] = [row.copy() for row in data["grid"]]
                
                # Créer les rotations possibles
                rotations = {}
                for angle in [0, 90, 180, 270]:
                    rotated_grid = apply_rotation_to_grid(data["original_grid"], angle)
                    rotations[str(angle)] = rotated_grid
                
                # Stocker les rotations dans les données du quadrant
                data["rotations"] = rotations
                need_save = True
        
        # Sauvegarder les modifications si nécessaire
        if need_save:
            json_path.write_text(json.dumps(quadrants_data, indent=4))
                
    quadrants = load_quadrants()
    
    # Ajout des orientations pour chaque quadrant
    prepare_rotated_grids(quadrants)
    
    # Charger les images des quadrants
    quadrant_images = {}
    for quadrant_id, data in quadrants.items():
        image_path = data.get("image_path")
        if image_path and Path(image_path).exists():
            img = pygame.image.load(image_path)
            quadrant_images[quadrant_id] = img
    
    # Calculer les dimensions pour le centrage de la zone du plateau et de la bibliothèque
    board_size = 400  # taille du plateau (carré)
    library_width = 310
    spacing = 30  # espacement entre les zones
    
    total_width = board_size + spacing + library_width
    total_height = board_size + 140  # hauteur du plateau + espace pour les boutons/titres
    
    # Positions centrées sur l'écran
    start_x = (WIDTH - total_width) // 2
    start_y = (HEIGHT - total_height) // 2 + 20  # un peu plus bas pour laisser de la place au titre
    
    # Définition des zones centrées
    board_area = pygame.Rect(start_x, start_y + 50, board_size, board_size)
    library_area = pygame.Rect(start_x + board_size + spacing, start_y + 50, library_width, board_size)
    
    # Position des emplacements des quadrants sur le plateau
    slot_size = board_size // 2
    quadrant_slots = [
        pygame.Rect(board_area.left, board_area.top, slot_size, slot_size),                             # Haut gauche
        pygame.Rect(board_area.left + slot_size, board_area.top, slot_size, slot_size),                 # Haut droite
        pygame.Rect(board_area.left, board_area.top + slot_size, slot_size, slot_size),                 # Bas gauche
        pygame.Rect(board_area.left + slot_size, board_area.top + slot_size, slot_size, slot_size)      # Bas droite
    ]
    
    # Quadrants sélectionnés (None = vide)
    selected_quadrants = [None, None, None, None]
    
    # Rotation des quadrants sélectionnés (0, 90, 180, 270 degrés)
    quadrant_rotations = [0, 0, 0, 0]
    
    # Position des boutons en bas (centrés)
    buttons_y = board_area.bottom + 20
    
    # Bouton commencer (centré)
    start_button_width = 200
    start_button_height = 50
    start_button = pygame.Rect(WIDTH//2 - start_button_width//2, buttons_y, start_button_width, start_button_height)
    
    # Bouton retour (à gauche)
    back_button_width = 120
    back_button_height = 50
    back_button = pygame.Rect(start_x, buttons_y, back_button_width, back_button_height)
    
    # Boutons de défilement pour la bibliothèque
    scroll_button_size = 30
    scroll_up_button = pygame.Rect(library_area.right - scroll_button_size - 5, library_area.top + 5, scroll_button_size, scroll_button_size)
    scroll_down_button = pygame.Rect(library_area.right - scroll_button_size - 5, library_area.bottom - scroll_button_size - 5, scroll_button_size, scroll_button_size)
    
    # Position de défilement de la bibliothèque
    scroll_y = 0
    scroll_speed = 15
    
    # Variables pour le glisser-déposer
    dragged_quadrant = None
    drag_offset_x = 0
    drag_offset_y = 0
    
    # Variables pour gérer le double-clic
    last_clicked_quadrant = None
    last_click_time = 0
    double_click_time = 300  # Temps maximum entre deux clics (en millisecondes)
    
    # Cache des images pivotées (pour meilleures performances)
    rotated_image_cache = {}
    
    # Fonction pour obtenir une image pivotée
    def get_rotated_image(image, angle):
        """Obtient une image pivotée, avec cache pour de meilleures performances"""
        cache_key = (id(image), angle)
        
        if cache_key not in rotated_image_cache:
            rotated_image_cache[cache_key] = pygame.transform.rotate(image, -angle)
            
        return rotated_image_cache[cache_key]
    
    # Génération des emplacements des quadrants dans la bibliothèque
    def generate_library_rects():
        rects = {}
        y_pos = library_area.top - scroll_y + 10
        thumbnail_size = 90
        
        items_per_row = 2
        item_width = (library_area.width - 40) // items_per_row
        
        row, col = 0, 0
        for quadrant_id in quadrants:
            # Ne montrer que les quadrants "de base" (sans suffixe de rotation)
            if not any(suffix in quadrant_id for suffix in ["_rot90", "_rot180", "_rot270"]):
                x = library_area.left + 10 + col * item_width
                y = y_pos + row * (thumbnail_size + 10)
                
                rect = pygame.Rect(x, y, thumbnail_size, thumbnail_size)
                rects[quadrant_id] = rect
                
                col += 1
                if col >= items_per_row:
                    col = 0
                    row += 1
            
        total_height = ((len(rects) + items_per_row - 1) // items_per_row) * (thumbnail_size + 10) + 10
        return rects, total_height
    
    def draw_quadrant_slot(slot_rect, quadrant_id, rotation=0, highlighted=False):
        """Dessine un slot avec ou sans quadrant, avec rotation éventuelle"""
        border_color = HIGHLIGHT if highlighted else DARK_GRAY
        
        pygame.draw.rect(screen, LIGHT_GRAY, slot_rect)
        pygame.draw.rect(screen, border_color, slot_rect, 3 if highlighted else 2)
        
        if quadrant_id and quadrant_id in quadrant_images:
            # Obtenir l'ID de base du quadrant (sans suffixe de rotation)
            base_quadrant_id = quadrant_id.split("_rot")[0]
            img = quadrant_images[base_quadrant_id] if base_quadrant_id in quadrant_images else quadrant_images[quadrant_id]
            
            # Obtenir l'image pivotée
            if rotation != 0:
                img = get_rotated_image(img, rotation)
                
            thumbnail = pygame.transform.scale(img, (slot_rect.width - 10, slot_rect.height - 10))
            img_rect = thumbnail.get_rect(center=slot_rect.center)
            screen.blit(thumbnail, img_rect.topleft)
            
            # Petit indicateur de numéro de quadrant
            q_num = base_quadrant_id.split('_')[1] if '_' in base_quadrant_id else quadrant_id.split('_')[1]
            num_font = pygame.font.Font(None, 20)
            num_text = num_font.render(q_num, True, BLACK)
            screen.blit(num_text, (slot_rect.right - num_text.get_width() - 5, slot_rect.bottom - num_text.get_height() - 5))
            
            # Indicateur de rotation (bien visible)
            if rotation != 0:
                rot_text = num_font.render(f"{rotation}°", True, (200, 0, 0))
                rot_rect = pygame.Rect(slot_rect.left + 5, slot_rect.bottom - 25, 40, 20)
                pygame.draw.rect(screen, (255, 255, 200), rot_rect)
                pygame.draw.rect(screen, (150, 0, 0), rot_rect, 1)
                screen.blit(rot_text, (slot_rect.left + 8, slot_rect.bottom - rot_text.get_height() - 8))
    
    def get_quadrant_grid(quadrant_id, rotation):
        """Obtient la grille du quadrant avec la rotation spécifiée"""
        base_id = quadrant_id.split("_rot")[0]
        
        if base_id in quadrants:
            if "rotations" in quadrants[base_id] and str(rotation) in quadrants[base_id]["rotations"]:
                return quadrants[base_id]["rotations"][str(rotation)]
            else:
                return apply_rotation_to_grid(quadrants[base_id].get("grid", []), rotation)
        
        return []
    
    def start_game_with_quadrants(selected_quadrants, rotations):
        """Démarre le jeu avec les quadrants sélectionnés et leurs rotations"""
        # Vérifier que les 4 quadrants sont sélectionnés
        if None in selected_quadrants:
            return False
        
        # Extraire les données de grille pour chaque quadrant avec sa rotation
        grid_data = []
        for i, quad_id in enumerate(selected_quadrants):
            if quad_id:
                grid = get_quadrant_grid(quad_id, rotations[i])
                grid_data.append(grid)
        
        # Vérifier que nous avons 4 grilles
        if len(grid_data) != 4:
            return False
        
        # Lancer le jeu avec les grilles des quadrants
        from plateau.game_board import start_game
        start_game(screen, grid_data)
        return True
    
    # Fonction pour afficher un message temporaire
    def show_message(message, duration=1000, color=(255, 0, 0)):
        font = pygame.font.Font(None, 36)
        text_surface = font.render(message, True, color)
        
        # Centrer le message sur l'écran
        text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
        
        # Créer un fond semi-transparent
        background = pygame.Surface((text_rect.width + 20, text_rect.height + 20), pygame.SRCALPHA)
        background.fill((0, 0, 0, 128))  # Fond noir semi-transparent
        background_rect = background.get_rect(center=text_rect.center)
        
        # Dessiner le fond et le texte
        screen.blit(background, background_rect)
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        
        pygame.time.delay(duration)
    
    # Boucle principale
    running = True
    
    while running:
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))
        
        # Titre centré
        title = title_font.render("Configuration de partie", True, BLACK)
        title_rect = title.get_rect(center=(WIDTH//2, start_y))
        screen.blit(title, title_rect)
        
        # Zone du plateau avec bordure
        pygame.draw.rect(screen, WHITE, board_area)
        pygame.draw.rect(screen, BLACK, board_area, 2)
        
        # Instructions pour le joueur (centrées sous le plateau)
        instruction_text = instruction_font.render("Double-clic pour tourner • Clic droit pour retirer", True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(board_area.centerx, board_area.bottom + 10))
        pygame.draw.rect(screen, WHITE, instruction_rect.inflate(8, 4))
        screen.blit(instruction_text, instruction_rect)
        
        # Zone de la bibliothèque avec bordure
        pygame.draw.rect(screen, WHITE, library_area)
        pygame.draw.rect(screen, BLACK, library_area, 2)
        
        # Titre de la bibliothèque (centré)
        lib_title = button_font.render("Bibliothèque", True, BLACK)
        lib_rect = lib_title.get_rect(center=(library_area.centerx, library_area.bottom + 20))
        lib_bg_rect = lib_rect.inflate(16, 8)
        lib_bg_surface = pygame.Surface(lib_bg_rect.size)
        lib_bg_surface.fill(WHITE)
        screen.blit(lib_bg_surface, lib_bg_rect)
        screen.blit(lib_title, lib_rect)
        
        # Déterminer le slot survolé
        hovered_slot = -1
        mouse_pos = pygame.mouse.get_pos()
        if dragged_quadrant:
            for i, slot in enumerate(quadrant_slots):
                if slot.collidepoint(mouse_pos):
                    hovered_slot = i
                    break
        
        # Dessiner les slots du plateau
        for i, (slot, quad_id) in enumerate(zip(quadrant_slots, selected_quadrants)):
            draw_quadrant_slot(slot, quad_id, quadrant_rotations[i], i == hovered_slot)
            
            # Numéro de slot
            slot_num = button_font.render(str(i+1), True, BLACK)
            slot_num_rect = slot_num.get_rect(topleft=(slot.left + 5, slot.top + 5))
            screen.blit(slot_num, slot_num_rect)
        
        # Dessiner la bibliothèque
        lib_rects, total_content_height = generate_library_rects()
        max_scroll = max(0, total_content_height - library_area.height)
        
        # Dessiner les quadrants visibles dans la bibliothèque
        for quadrant_id, rect in lib_rects.items():
            # Vérifier si le quadrant est à l'intérieur de library_area
            if rect.top < library_area.bottom and rect.bottom > library_area.top:
                visible_rect = rect.clip(library_area)
                if visible_rect.height > 0:
                    # Si le quadrant est en cours de déplacement, ne pas le dessiner dans la bibliothèque
                    if dragged_quadrant != quadrant_id:
                        # Dessiner le fond du quadrant
                        pygame.draw.rect(screen, LIGHT_GRAY, visible_rect)
                        pygame.draw.rect(screen, DARK_GRAY, visible_rect, 2)
                        
                        # Dessiner l'image miniature
                        if quadrant_id in quadrant_images:
                            img = quadrant_images[quadrant_id]
                            thumbnail = pygame.transform.scale(img, (rect.width - 10, rect.height - 10))
                            img_rect = thumbnail.get_rect(center=rect.center)
                            
                            # Ajuster l'image pour qu'elle soit visible seulement dans library_area
                            src_rect = pygame.Rect(0, 0, thumbnail.get_width(), thumbnail.get_height())
                            if img_rect.top < library_area.top:
                                src_rect.top = library_area.top - img_rect.top
                                img_rect.top = library_area.top
                            if img_rect.bottom > library_area.bottom:
                                src_rect.height = library_area.bottom - img_rect.top
                            
                            if src_rect.height > 0:
                                screen.blit(thumbnail, img_rect.topleft, src_rect)
                        
                        # Numéro du quadrant (seulement s'il est complètement visible)
                        if rect.bottom <= library_area.bottom:
                            q_num = quadrant_id.split('_')[1]
                            num_font = pygame.font.Font(None, 20)
                            num_text = num_font.render(q_num, True, BLACK)
                            screen.blit(num_text, (rect.right - num_text.get_width() - 5, rect.bottom - num_text.get_height() - 5))
        
        # Dessiner les boutons de défilement
        pygame.draw.rect(screen, DARK_GRAY, scroll_up_button)
        pygame.draw.rect(screen, DARK_GRAY, scroll_down_button)
        
        # Flèches pour les boutons de défilement
        pygame.draw.polygon(screen, WHITE, [
            (scroll_up_button.centerx, scroll_up_button.top + 5),
            (scroll_up_button.left + 5, scroll_up_button.bottom - 5),
            (scroll_up_button.right - 5, scroll_up_button.bottom - 5)
        ])
        pygame.draw.polygon(screen, WHITE, [
            (scroll_down_button.centerx, scroll_down_button.bottom - 5),
            (scroll_down_button.left + 5, scroll_down_button.top + 5),
            (scroll_down_button.right - 5, scroll_down_button.top + 5)
        ])
        
        # Dessiner le quadrant actuellement déplacé
        if dragged_quadrant and dragged_quadrant in quadrant_images:
            base_quadrant_id = dragged_quadrant.split("_rot")[0]
            img = quadrant_images[base_quadrant_id] if base_quadrant_id in quadrant_images else quadrant_images[dragged_quadrant]
            
            drag_size = 150
            thumbnail = pygame.transform.scale(img, (drag_size, drag_size))
            img_rect = thumbnail.get_rect(center=(mouse_pos[0] - drag_offset_x, mouse_pos[1] - drag_offset_y))
            screen.blit(thumbnail, img_rect.topleft)
            
            # Indicateur de numéro
            q_num = dragged_quadrant.split('_')[1]
            num_font = pygame.font.Font(None, 20)
            num_text = num_font.render(q_num, True, BLACK)
            screen.blit(num_text, (img_rect.right - num_text.get_width() - 5, img_rect.bottom - num_text.get_height() - 5))
        
        # Dessiner le bouton Commencer
        all_selected = None not in selected_quadrants
        pygame.draw.rect(screen, BLUE if all_selected else DARK_GRAY, start_button)
        start_text = button_font.render("Commencer", True, BLACK)
        start_text_rect = start_text.get_rect(center=start_button.center)
        screen.blit(start_text, start_text_rect)
        
        # Bouton retour
        pygame.draw.rect(screen, RED, back_button)
        back_text = button_font.render("Retour", True, BLACK)
        back_text_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, back_text_rect)
        
        # Traitement des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Clic droit pour retirer un quadrant sans le prendre en main
                if event.button == 3:  # Bouton droit
                    for i, slot in enumerate(quadrant_slots):
                        if slot.collidepoint(event.pos) and selected_quadrants[i] is not None:
                            selected_quadrants[i] = None
                            quadrant_rotations[i] = 0
                            break
                
                # Clic gauche pour les interactions standard
                elif event.button == 1:
                    # Clic sur le bouton retour
                    if back_button.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')  # ✅ NOUVEAU SON
                        return
                    
                    # Clic sur le bouton commencer
                    if start_button.collidepoint(event.pos) and all_selected:
                        audio_manager.play_sound('button_click')  # ✅ NOUVEAU SON
                        start_game_with_quadrants(selected_quadrants, quadrant_rotations)
                        # Recharger les quadrants après le jeu
                        quadrants = load_quadrants()
                    
                    # Clic sur les boutons de défilement
                    if scroll_up_button.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')  # ✅ NOUVEAU SON
                        scroll_y = max(0, scroll_y - scroll_speed)
                    elif scroll_down_button.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')  # ✅ NOUVEAU SON
                        scroll_y = min(max_scroll, scroll_y + scroll_speed)
                    
                    # Vérifier les clics sur les slots du plateau
                    for i, slot in enumerate(quadrant_slots):
                        if slot.collidepoint(event.pos):
                            # Vérifier s'il s'agit d'un double-clic (pour la rotation)
                            current_time = pygame.time.get_ticks()
                            if last_clicked_quadrant == f"slot_{i}" and (current_time - last_click_time) < double_click_time:
                                if selected_quadrants[i]:
                                    # Faire pivoter le quadrant à 90 degrés
                                    quadrant_rotations[i] = (quadrant_rotations[i] + 90) % 360
                                break
                            
                            # Enregistrer pour la détection du prochain double-clic
                            last_clicked_quadrant = f"slot_{i}"
                            last_click_time = current_time
                            
                            # Si ce n'est pas un double-clic et qu'il y a un quadrant, le prendre
                            if selected_quadrants[i] and not (last_clicked_quadrant == f"slot_{i}" and 
                                                           (current_time - last_click_time) < double_click_time):
                                dragged_quadrant = selected_quadrants[i]
                                selected_quadrants[i] = None
                                quadrant_rotations[i] = 0
                                drag_offset_x = event.pos[0] - slot.centerx
                                drag_offset_y = event.pos[1] - slot.centery
                            break
                    
                    # Vérifier les clics sur les quadrants de la bibliothèque
                    if not dragged_quadrant:  # Si on n'a pas déjà un quadrant en main
                        for quad_id, rect in lib_rects.items():
                            if rect.collidepoint(event.pos) and rect.top >= library_area.top and rect.bottom <= library_area.bottom:
                                dragged_quadrant = quad_id
                                drag_offset_x = event.pos[0] - rect.centerx
                                drag_offset_y = event.pos[1] - rect.centery
                                break
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragged_quadrant:  # Relâcher un quadrant
                    # Vérifier si on relâche sur un slot
                    dropped_in_slot = False
                    for i, slot in enumerate(quadrant_slots):
                        if slot.collidepoint(event.pos):
                            # Permuter si le slot contient déjà un quadrant
                            old_quad = selected_quadrants[i]
                            selected_quadrants[i] = dragged_quadrant
                            
                            # Réinitialiser la rotation pour le nouveau quadrant
                            quadrant_rotations[i] = 0
                            
                            dragged_quadrant = old_quad  # Prendre l'ancien quadrant ou None
                            dropped_in_slot = True
                            break
                    
                    # Si on n'a pas relâché sur un slot, remettre dans la bibliothèque
                    if not dropped_in_slot:
                        dragged_quadrant = None
            
            elif event.type == pygame.MOUSEWHEEL and library_area.collidepoint(pygame.mouse.get_pos()):
                scroll_y = max(0, min(max_scroll, scroll_y - event.y * scroll_speed))
        
        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    show_game_setup(screen)
    pygame.quit()