import pygame
import sys
from pathlib import Path
from quadrant_viewer import load_quadrants
from assets.colors import Colors

def show_network_quadrant_setup(screen, network_manager, is_server):
    """
    Interface pour que chaque joueur configure SES quadrants
    """
    
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    
    # Définir quel joueur configure quels quadrants
    if is_server:
        pygame.display.set_caption("Configuration - Joueur Rouge (Haut)")
        my_color = "Rouge"
        quadrant_positions = ["Haut Gauche", "Haut Droite"]
        quadrant_indices = [0, 1]  # Quadrants 1 et 2
        player_color = (200, 50, 50)
    else:
        pygame.display.set_caption("Configuration - Joueur Bleu (Bas)")
        my_color = "Bleu"
        quadrant_positions = ["Bas Gauche", "Bas Droite"]  
        quadrant_indices = [2, 3]  # Quadrants 3 et 4
        player_color = (50, 50, 200)
    
    # Couleurs
    script_dir = Path(sys.argv[0]).parent.absolute()
    background_image = pygame.image.load(str(script_dir / "assets" / "img" / "fond.png"))
    WHITE = Colors.WHITE
    BLACK = Colors.BLACK
    LIGHT_GRAY = Colors.LIGHT_GRAY
    DARK_GRAY = Colors.DARK_GRAY
    BLUE = Colors.BLUE
    RED = Colors.RED
    GREEN = Colors.GREEN
    HIGHLIGHT = Colors.HIGHLIGHT
    
    # Polices
    title_font = pygame.font.Font(None, 36)
    button_font = pygame.font.Font(None, 30)
    instruction_font = pygame.font.Font(None, 20)
    
    # Charger les quadrants disponibles
    quadrants = load_quadrants()
    
    # Charger les images des quadrants
    quadrant_images = {}
    for quadrant_id, data in quadrants.items():
        image_path = data.get("image_path")
        if image_path:
            path_obj = Path(image_path)
            if path_obj.exists():
                img = pygame.image.load(str(path_obj))
                quadrant_images[quadrant_id] = img
    
    # Configuration de l'interface - plus compacte
    preview_size = 150  # Taille des aperçus
    library_width = 250
    spacing = 20
    
    # Zone de prévisualisation (côté joueur)
    preview_area = pygame.Rect(50, HEIGHT // 4, preview_size * 2 + spacing, preview_size + 100)
    
    # Zone de la bibliothèque  
    library_area = pygame.Rect(WIDTH - library_width - 30, HEIGHT // 6, library_width, HEIGHT - HEIGHT // 3)
    
    # Positions des slots de prévisualisation
    preview_slots = []
    for i in range(2):
        x = preview_area.left + i  * (preview_size + spacing) + 600
        y = preview_area.top + 150
        slot = pygame.Rect(x, y, preview_size, preview_size)
        preview_slots.append(slot)
    
    # Quadrants sélectionnés par ce joueur
    selected_quadrants = [None, None]  # 2 quadrants par joueur
    quadrant_rotations = [0, 0]
    
    # Variables pour le glisser-déposer
    dragged_quadrant = None
    drag_offset_x = 0
    drag_offset_y = 0
    
    # Variables pour la gestion du double-clic (rotation)
    last_clicked_quadrant = None
    last_click_time = 0
    double_click_time = 300
    
    # Cache des images pivotées
    rotated_image_cache = {}
    
    # Position de défilement de la bibliothèque
    scroll_y = 0
    scroll_speed = 20
    
    def get_rotated_image(image, angle):
        """Obtient une image pivotée avec cache"""
        cache_key = (id(image), angle)
        if cache_key not in rotated_image_cache:
            rotated_image_cache[cache_key] = pygame.transform.rotate(image, -angle)
        return rotated_image_cache[cache_key]
    
    def generate_library_rects():
        """Génère les rectangles de la bibliothèque avec défilement"""
        rects = {}
        y_pos = library_area.top - scroll_y + 10
        thumbnail_size = 80
        
        items_per_row = 2
        item_width = (library_area.width - 30) // items_per_row
        
        row, col = 0, 0
        for quadrant_id in quadrants:
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
    
    def draw_preview_slot(slot_rect, quadrant_id, rotation, slot_index, highlighted=False):
        """Dessine un slot de prévisualisation avec fond blanc sous le label"""
        border_color = HIGHLIGHT if highlighted else player_color

        # Dessin du slot
        pygame.draw.rect(screen, LIGHT_GRAY, slot_rect)
        pygame.draw.rect(screen, border_color, slot_rect, 3 if highlighted else 2)

        # Label du slot avec fond blanc
        label_text = quadrant_positions[slot_index]
        label_surface = instruction_font.render(label_text, True, BLACK)
        label_rect = label_surface.get_rect(centerx=slot_rect.centerx, bottom=slot_rect.top - 5)

        # Fond blanc sous le label
        padding = 6
        bg_rect = pygame.Rect(
            label_rect.left - padding,
            label_rect.top - padding,
            label_rect.width + 2 * padding,
            label_rect.height + 2 * padding
        )
        pygame.draw.rect(screen, WHITE, bg_rect)
        screen.blit(label_surface, label_rect)

        # Affichage de l'image du quadrant si présente
        if quadrant_id and quadrant_id in quadrant_images:
            img = quadrant_images[quadrant_id]
            # Appliquer la rotation si besoin
            if rotation != 0:
                img = get_rotated_image(img, rotation)
            thumbnail = pygame.transform.scale(img, (slot_rect.width - 10, slot_rect.height - 10))
            img_rect = thumbnail.get_rect(center=slot_rect.center)
            screen.blit(thumbnail, img_rect.topleft)

            # Numéro de quadrant
            q_num = quadrant_id.split('_')[1]
            num_font = pygame.font.Font(None, 20)
            num_text = num_font.render(q_num, True, BLACK)
            screen.blit(num_text, (slot_rect.right - num_text.get_width() - 5, slot_rect.bottom - num_text.get_height() - 5))

            # Indicateur de rotation
            if rotation != 0:
                rot_text = num_font.render(f"{rotation}°", True, (200, 0, 0))
                rot_rect = pygame.Rect(slot_rect.left + 5, slot_rect.bottom - 25, 40, 20)
                pygame.draw.rect(screen, (255, 255, 200), rot_rect)
                pygame.draw.rect(screen, (150, 0, 0), rot_rect, 1)
                screen.blit(rot_text, (slot_rect.left + 8, slot_rect.bottom - rot_text.get_height() - 8))
    
    def apply_rotation_to_grid(grid, rotation):
        """
        Applique une rotation à une grille
        """
        rotated_grid = [row.copy() for row in grid]
        num_rotations = rotation // 90
        for _ in range(num_rotations):
            rows = len(rotated_grid)
            cols = len(rotated_grid[0])
            new_grid = [[0 for _ in range(rows)] for _ in range(cols)]
            for i in range(rows):
                for j in range(cols):
                    new_grid[j][rows - 1 - i] = rotated_grid[i][j]
            rotated_grid = new_grid
        return rotated_grid
    
    def get_quadrant_grid(quadrant_id, rotation):
        """Obtient la grille du quadrant avec rotation"""
        if quadrant_id in quadrants:
            original_grid = quadrants[quadrant_id].get("grid", [])
            return apply_rotation_to_grid(original_grid, rotation)
        return []
    
    def send_my_quadrants():
        """Envoie la configuration de mes quadrants à l'adversaire"""
        if None in selected_quadrants:
            return False
        
        my_config = []
        for i, quad_id in enumerate(selected_quadrants):
            grid = get_quadrant_grid(quad_id, quadrant_rotations[i])
            my_config.append(grid)
        
        message_data = {
            "player": "server" if is_server else "client",
            "quadrants": my_config,
            "quadrant_indices": quadrant_indices  # Positions dans le plateau final
        }
        
        network_manager.send_message("quadrant_config", message_data)
        print(f"Configuration envoyée: {len(my_config)} quadrants")
        return True
    
    def send_ready_signal():
        """Signale qu'on est prêt à jouer"""
        network_manager.send_message("game_ready", {"player": "server" if is_server else "client"})
        print("Signal de jeu envoyé")
    
    # Boutons
    button_y = HEIGHT - 80
    ready_button = pygame.Rect(WIDTH // 2 - 100, button_y, 200, 50)
    
    # Variables d'état
    configuration_sent = False
    opponent_config = None
    waiting_for_opponent = False
    both_ready = False  # Nouveau : les deux joueurs ont envoyé leur config
    
    # Boucle principale
    running = True
    clock = pygame.time.Clock()
    
    while running:
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))
        
        # Titre
        title = title_font.render(f"Configuration - Joueur {my_color}", True, player_color)
        title_rect = title.get_rect(center=(WIDTH // 2, 50))
        screen.blit(title, title_rect)
        
        # Instructions
        instruction = instruction_font.render("Configurez vos 2 quadrants • Double-clic pour tourner • Clic droit pour retirer", True, BLACK)
        instruction_rect = instruction.get_rect(center=(WIDTH // 2, 90))
        screen.blit(instruction, instruction_rect)
        
        # Déterminer le slot survolé
        hovered_slot = -1
        mouse_pos = pygame.mouse.get_pos()
        if dragged_quadrant:
            for i, slot in enumerate(preview_slots):
                if slot.collidepoint(mouse_pos):
                    hovered_slot = i
                    break
        
        # Dessiner les slots de prévisualisation
        for i, slot in enumerate(preview_slots):
            draw_preview_slot(slot, selected_quadrants[i], quadrant_rotations[i], i, i == hovered_slot)
        
        # Zone de la bibliothèque
        pygame.draw.rect(screen, WHITE, library_area)
        pygame.draw.rect(screen, BLACK, library_area, 2)
        
        lib_title = button_font.render("Bibliothèque", True, BLACK)
        lib_rect = lib_title.get_rect(center=(library_area.centerx, library_area.top - 15))
        screen.blit(lib_title, lib_rect)
        
        # Dessiner la bibliothèque
        lib_rects, total_content_height = generate_library_rects()
        max_scroll = max(0, total_content_height - library_area.height)
        
        for quadrant_id, rect in lib_rects.items():
            if rect.top < library_area.bottom and rect.bottom > library_area.top:
                visible_rect = rect.clip(library_area)
                if visible_rect.height > 0 and dragged_quadrant != quadrant_id:
                    pygame.draw.rect(screen, LIGHT_GRAY, visible_rect)
                    pygame.draw.rect(screen, DARK_GRAY, visible_rect, 2)
                    
                    if quadrant_id in quadrant_images:
                        img = quadrant_images[quadrant_id]
                        thumbnail = pygame.transform.scale(img, (rect.width - 6, rect.height - 6))
                        img_rect = thumbnail.get_rect(center=rect.center)
                        
                        # Clipping pour la zone visible
                        if img_rect.top < library_area.top:
                            crop_top = library_area.top - img_rect.top
                            img_rect.top = library_area.top
                            thumbnail = thumbnail.subsurface(0, crop_top, thumbnail.get_width(), thumbnail.get_height() - crop_top)
                        
                        if img_rect.bottom > library_area.bottom:
                            crop_bottom = img_rect.bottom - library_area.bottom
                            thumbnail = thumbnail.subsurface(0, 0, thumbnail.get_width(), thumbnail.get_height() - crop_bottom)
                        
                        if thumbnail.get_height() > 0:
                            screen.blit(thumbnail, img_rect.topleft)
                    
                    # Numéro du quadrant
                    if rect.bottom <= library_area.bottom:
                        q_num = quadrant_id.split('_')[1]
                        num_font = pygame.font.Font(None, 16)
                        num_text = num_font.render(q_num, True, BLACK)
                        screen.blit(num_text, (rect.right - num_text.get_width() - 3, rect.bottom - num_text.get_height() - 3))
        
        # Dessiner le quadrant en cours de déplacement
        if dragged_quadrant and dragged_quadrant in quadrant_images:
            img = quadrant_images[dragged_quadrant]
            drag_size = 100
            thumbnail = pygame.transform.scale(img, (drag_size, drag_size))
            img_rect = thumbnail.get_rect(center=(mouse_pos[0] - drag_offset_x, mouse_pos[1] - drag_offset_y))
            screen.blit(thumbnail, img_rect.topleft)
        
        # Bouton "Prêt"
        all_selected = None not in selected_quadrants
        button_color = GREEN if all_selected and not configuration_sent else DARK_GRAY
        button_text = "Configuration envoyée" if configuration_sent else ("Prêt !" if all_selected else "Sélectionnez 2 quadrants")
        
        pygame.draw.rect(screen, button_color, ready_button)
        pygame.draw.rect(screen, BLACK, ready_button, 2)
        
        text_surf = button_font.render(button_text, True, BLACK)
        text_rect = text_surf.get_rect(center=ready_button.center)
        screen.blit(text_surf, text_rect)
        
        # Messages d'état
        if waiting_for_opponent:
            wait_text = instruction_font.render("En attente de la configuration de l'adversaire...", True, (100, 100, 100))
            wait_rect = wait_text.get_rect(center=(WIDTH // 2, button_y - 30))
            screen.blit(wait_text, wait_rect)
        
        elif configuration_sent and not opponent_config:
            ready_text = instruction_font.render("Configuration envoyée ! En attente de l'adversaire...", True, (0, 150, 0))
            ready_rect = ready_text.get_rect(center=(WIDTH // 2, button_y - 30))
            screen.blit(ready_text, ready_rect)
        
        # Vérifier les messages réseau
        messages = network_manager.get_messages()
        for message in messages:
            if message['type'] == 'quadrant_config':
                opponent_config = message['data']
                print(f"Configuration reçue de l'adversaire")
                
                # Si j'ai déjà envoyé ma config, on peut démarrer
                if configuration_sent:
                    print("Les deux configurations sont prêtes - Démarrage du jeu")
                    both_ready = True
                    send_ready_signal()  # Confirmer qu'on est prêt
                    return build_final_board_config(selected_quadrants, quadrant_rotations, opponent_config, is_server)
            
            elif message['type'] == 'game_ready':
                # L'adversaire confirme qu'il est prêt à jouer
                print("Confirmation de jeu reçue de l'adversaire")
                if configuration_sent and opponent_config:
                    print("Tout est prêt - Démarrage du jeu")
                    return build_final_board_config(selected_quadrants, quadrant_rotations, opponent_config, is_server)
        
        # Traitement des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Clic droit - retirer un quadrant
                    for i, slot in enumerate(preview_slots):
                        if slot.collidepoint(event.pos) and selected_quadrants[i] is not None:
                            selected_quadrants[i] = None
                            quadrant_rotations[i] = 0
                            configuration_sent = False
                            break
                
                elif event.button == 1:  # Clic gauche
                    # Bouton "Prêt"
                    if ready_button.collidepoint(event.pos) and all_selected and not configuration_sent:
                        if send_my_quadrants():
                            configuration_sent = True
                            waiting_for_opponent = True
                            
                            # Si on a déjà reçu la config de l'adversaire, on peut démarrer immédiatement
                            if opponent_config:
                                print("Config adversaire déjà reçue - Démarrage immédiat")
                                send_ready_signal()  # Signaler qu'on est prêt
                                return build_final_board_config(selected_quadrants, quadrant_rotations, opponent_config, is_server)
                            else:
                                print("En attente de la configuration de l'adversaire")
                    
                    # Gestion du double-clic pour rotation
                    current_time = pygame.time.get_ticks()
                    clicked_slot = None
                    for i, slot in enumerate(preview_slots):
                        if slot.collidepoint(event.pos):
                            clicked_slot = f"slot_{i}"
                            if (last_clicked_quadrant == clicked_slot and 
                                (current_time - last_click_time) < double_click_time and 
                                selected_quadrants[i]):
                                # Double-clic détecté - rotation
                                quadrant_rotations[i] = (quadrant_rotations[i] + 90) % 360
                                configuration_sent = False
                                break
                            elif selected_quadrants[i]:
                                # Premier clic - prendre le quadrant
                                dragged_quadrant = selected_quadrants[i]
                                selected_quadrants[i] = None
                                quadrant_rotations[i] = 0
                                configuration_sent = False
                                drag_offset_x = event.pos[0] - slot.centerx
                                drag_offset_y = event.pos[1] - slot.centery
                            break
                    
                    last_clicked_quadrant = clicked_slot
                    last_click_time = current_time
                    
                    # Clic sur la bibliothèque
                    if not dragged_quadrant:
                        for quad_id, rect in lib_rects.items():
                            if (rect.collidepoint(event.pos) and 
                                rect.top >= library_area.top and rect.bottom <= library_area.bottom):
                                dragged_quadrant = quad_id
                                drag_offset_x = event.pos[0] - rect.centerx
                                drag_offset_y = event.pos[1] - rect.centery
                                break
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragged_quadrant:
                    # Relâcher sur un slot
                    dropped = False
                    for i, slot in enumerate(preview_slots):
                        if slot.collidepoint(event.pos):
                            old_quad = selected_quadrants[i]
                            selected_quadrants[i] = dragged_quadrant
                            quadrant_rotations[i] = 0
                            dragged_quadrant = old_quad
                            configuration_sent = False
                            dropped = True
                            break
                    
                    if not dropped:
                        dragged_quadrant = None
            
            elif event.type == pygame.MOUSEWHEEL:
                if library_area.collidepoint(pygame.mouse.get_pos()):
                    scroll_y = max(0, min(max_scroll, scroll_y - event.y * scroll_speed))
        
        pygame.display.flip()
        clock.tick(60)
    
    return None

def build_final_board_config(my_quadrants, my_rotations, opponent_config, is_server):
    """
    Construit la configuration finale du plateau
    """
    
    def apply_rotation_to_grid(grid, rotation):
        rotated_grid = [row.copy() for row in grid]
        num_rotations = rotation // 90
        for _ in range(num_rotations):
            rows = len(rotated_grid)
            cols = len(rotated_grid[0])
            new_grid = [[0 for i in range(rows)] for j in range(cols)]
            for i in range(rows):
                for j in range(cols):
                    new_grid[j][rows - 1 - i] = rotated_grid[i][j]
            rotated_grid = new_grid
        return rotated_grid
    
    def get_quadrant_grid(quadrant_id, rotation):
        quadrants = load_quadrants()
        if quadrant_id in quadrants:
            original_grid = quadrants[quadrant_id].get("grid", [])
            return apply_rotation_to_grid(original_grid, rotation)
        return []
    
    # Construire ma configuration
    my_grids = []
    for i, quad_id in enumerate(my_quadrants):
        grid = get_quadrant_grid(quad_id, my_rotations[i])
        my_grids.append(grid)
    
    # Récupérer la configuration de l'adversaire
    opponent_grids = opponent_config['quadrants']
    
    # Assembler le plateau final
    final_quadrants = [None, None, None, None]
    
    if is_server:
        # Serveur: mes quadrants en haut (0,1), adversaire en bas (2,3)
        final_quadrants[0] = my_grids[0]      # Haut gauche
        final_quadrants[1] = my_grids[1]      # Haut droite  
        final_quadrants[2] = opponent_grids[0] # Bas gauche
        final_quadrants[3] = opponent_grids[1] # Bas droite
    else:
        # Client: adversaire en haut (0,1), mes quadrants en bas (2,3)
        final_quadrants[0] = opponent_grids[0] # Haut gauche
        final_quadrants[1] = opponent_grids[1] # Haut droite
        final_quadrants[2] = my_grids[0]      # Bas gauche
        final_quadrants[3] = my_grids[1]      # Bas droite
    
    print(f"Plateau final assemblé: {'Serveur' if is_server else 'Client'}")
    return final_quadrants