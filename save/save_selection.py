import pygame
import sys
from pathlib import Path
from assets.colors import Colors
from save.save_game import save_manager

def show_game_selection(screen):
    """
    Affiche l'écran de sélection entre nouvelle partie et partie sauvegardée
    
    Returns:
        str: "new_game", "load_game", ou "back"
    """
    # Couleurs
    WHITE = Colors.WHITE
    BLACK = Colors.BLACK
    BLUE = Colors.BLUE
    RED = Colors.RED
    GREEN = Colors.GREEN
    GRAY = Colors.GRAY
    
    # Chargement de l'image de fond
    script_dir = Path(sys.argv[0]).parent.absolute()
    background_image = pygame.image.load(script_dir / "assets" / "img" / "fond.png")
    
    # Polices
    title_font = pygame.font.Font(None, 64)
    button_font = pygame.font.Font(None, 32)
    info_font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        current_width, current_height = screen.get_size()
        
        # Redimensionner et afficher le fond
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))
        
        # Titre
        title_text = title_font.render("Lancer une partie", True, BLACK)
        title_rect = title_text.get_rect(center=(current_width // 2, current_height // 4))
        screen.blit(title_text, title_rect)
        
        # Dimensions des boutons
        button_width = 300
        button_height = 60
        button_spacing = 30
        
        # Position centrale des boutons
        center_x = current_width // 2
        center_y = current_height // 2
        
        # Bouton Nouvelle Partie
        new_game_button = pygame.Rect(
            center_x - button_width // 2,
            center_y - button_height - button_spacing // 2,
            button_width,
            button_height
        )
        
        # Bouton Charger Partie
        load_game_button = pygame.Rect(
            center_x - button_width // 2,
            center_y + button_spacing // 2,
            button_width,
            button_height
        )
        
        # Bouton Retour
        back_button = pygame.Rect(50, 50, 100, 40)
        
        # Vérifier s'il y a une sauvegarde
        has_save = save_manager.has_save()
        save_info = save_manager.get_save_info() if has_save else None
        
        # Dessiner le bouton Nouvelle Partie
        pygame.draw.rect(screen, GREEN, new_game_button)
        pygame.draw.rect(screen, BLACK, new_game_button, 3)
        
        new_game_text = button_font.render("Nouvelle Partie", True, WHITE)
        new_game_text_rect = new_game_text.get_rect(center=new_game_button.center)
        screen.blit(new_game_text, new_game_text_rect)
        
        # Dessiner le bouton Charger Partie
        if has_save:
            pygame.draw.rect(screen, BLUE, load_game_button)
            pygame.draw.rect(screen, BLACK, load_game_button, 3)
            
            load_game_text = button_font.render("Charger Partie", True, WHITE)
            load_game_text_rect = load_game_text.get_rect(center=load_game_button.center)
            screen.blit(load_game_text, load_game_text_rect)
            
            # Afficher les informations de la sauvegarde
            if save_info:
                info_y = load_game_button.bottom + 20
                
                # Convertir le mode en nom lisible
                mode_names = {0: "Katarenga", 1: "Congress", 2: "Isolation"}
                mode_name = mode_names.get(save_info['mode'], f"Mode {save_info['mode']}")
                
                mode_text = info_font.render(f"Mode: {mode_name}", True, BLACK)
                mode_rect = mode_text.get_rect(center=(center_x, info_y))
                screen.blit(mode_text, mode_rect)
                
                player_text = info_font.render(
                    f"Tour: Joueur {'Rouge' if save_info['current_player'] == 1 else 'Bleu'}", 
                    True, BLACK
                )
                player_rect = player_text.get_rect(center=(center_x, info_y + 25))
                screen.blit(player_text, player_rect)
                
                # Formater la date
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(save_info['save_date'])
                    date_str = date_obj.strftime("%d/%m/%Y à %H:%M")
                except:
                    date_str = "Date inconnue"
                
                date_text = info_font.render(f"Sauvegardé le: {date_str}", True, GRAY)
                date_rect = date_text.get_rect(center=(center_x, info_y + 50))
                screen.blit(date_text, date_rect)
        else:
            # Bouton désactivé
            pygame.draw.rect(screen, GRAY, load_game_button)
            pygame.draw.rect(screen, BLACK, load_game_button, 3)
            
            load_game_text = button_font.render("Aucune sauvegarde", True, BLACK)
            load_game_text_rect = load_game_text.get_rect(center=load_game_button.center)
            screen.blit(load_game_text, load_game_text_rect)
        
        # Dessiner le bouton Retour
        pygame.draw.rect(screen, RED, back_button)
        pygame.draw.rect(screen, BLACK, back_button, 2)
        
        back_text = button_font.render("Retour", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, back_text_rect)
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.collidepoint(event.pos):
                    return "new_game"
                elif load_game_button.collidepoint(event.pos) and has_save:
                    return "load_game"
                elif back_button.collidepoint(event.pos):
                    return "back"
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                elif event.key == pygame.K_1:
                    return "new_game"
                elif event.key == pygame.K_2 and has_save:
                    return "load_game"
        
        pygame.display.flip()
        clock.tick(60)
    
    return "back"