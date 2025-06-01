import pygame
import sys
from pathlib import Path
from assets.colors import Colors
from assets.audio_manager import audio_manager

def show_settings_menu(screen):
    """
    Affiche la page des paramètres
    """
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    pygame.display.set_caption("Paramètres")
    
    # Couleurs
    script_dir = Path(__file__).parent.parent.absolute()
    background_image = pygame.image.load(script_dir / "assets" / "img" / "fond.png")
    
    WHITE = Colors.WHITE
    BLACK = Colors.BLACK
    BLUE = Colors.BLUE
    RED = Colors.RED
    GREEN = Colors.GREEN
    LIGHT_GRAY = Colors.LIGHT_GRAY
    DARK_GRAY = Colors.DARK_GRAY
    
    # Polices
    title_font = pygame.font.Font(None, 48)
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    # Configuration des éléments
    center_x = WIDTH // 2
    start_y = HEIGHT // 3
    spacing = 80
    
    # Boutons et éléments
    audio_toggle_rect = pygame.Rect(center_x - 150, start_y, 300, 50)
    volume_slider_rect = pygame.Rect(center_x - 150, start_y + spacing, 300, 20)
    volume_handle_size = 30
    
    test_button_rect = pygame.Rect(center_x - 100, start_y + spacing * 2, 200, 50)
    back_button_rect = pygame.Rect(center_x - 100, start_y + spacing * 3, 200, 50)
    
    # Variables pour le slider
    dragging_volume = False
    
    def draw_volume_slider(screen, volume):
        """Dessine le slider de volume"""
        # Barre de fond
        pygame.draw.rect(screen, DARK_GRAY, volume_slider_rect)
        pygame.draw.rect(screen, BLACK, volume_slider_rect, 2)
        
        # Position du curseur
        handle_x = volume_slider_rect.x + (volume * volume_slider_rect.width) - volume_handle_size // 2
        handle_y = volume_slider_rect.y - (volume_handle_size - volume_slider_rect.height) // 2
        handle_rect = pygame.Rect(handle_x, handle_y, volume_handle_size, volume_handle_size)
        
        # Curseur
        pygame.draw.circle(screen, BLUE, handle_rect.center, volume_handle_size // 2)
        pygame.draw.circle(screen, BLACK, handle_rect.center, volume_handle_size // 2, 2)
        
        # Texte du volume - CORRIGÉ: position plus basse pour éviter le chevauchement
        volume_text = small_font.render(f"Volume: {int(volume * 100)}%", True, BLACK)
        volume_text_rect = volume_text.get_rect(center=(center_x, volume_slider_rect.y + 45))
        screen.blit(volume_text, volume_text_rect)
        
        return handle_rect
    
    def update_volume_from_mouse(mouse_x):
        """Met à jour le volume basé sur la position de la souris"""
        relative_x = mouse_x - volume_slider_rect.x
        volume = max(0.0, min(1.0, relative_x / volume_slider_rect.width))
        audio_manager.set_volume(volume)
        return volume
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Fond
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))
        
        # Titre
        title = title_font.render("Paramètres", True, BLACK)
        title_rect = title.get_rect(center=(center_x, HEIGHT // 6))
        
        # Fond semi-transparent pour le titre
        bg_surface = pygame.Surface((title_rect.width + 20, title_rect.height + 10), pygame.SRCALPHA)
        bg_surface.fill((255, 255, 255, 200))
        screen.blit(bg_surface, (title_rect.x - 10, title_rect.y - 5))
        screen.blit(title, title_rect)
        
        # Section Audio
        audio_section = font.render("Audio", True, BLACK)
        audio_rect = audio_section.get_rect(center=(center_x, start_y - 40))
        screen.blit(audio_section, audio_rect)
        
        # Bouton toggle audio
        is_enabled = audio_manager.is_enabled()
        toggle_color = GREEN if is_enabled else RED
        toggle_text = "Audio: Activé" if is_enabled else "Audio: Désactivé"
        
        pygame.draw.rect(screen, toggle_color, audio_toggle_rect)
        pygame.draw.rect(screen, BLACK, audio_toggle_rect, 2)
        
        toggle_surface = font.render(toggle_text, True, BLACK)
        toggle_text_rect = toggle_surface.get_rect(center=audio_toggle_rect.center)
        screen.blit(toggle_surface, toggle_text_rect)
        
        # Slider de volume (seulement si audio activé)
        current_volume = audio_manager.settings['volume']
        if is_enabled:
            volume_handle_rect = draw_volume_slider(screen, current_volume)
        else:
            # Slider grisé
            pygame.draw.rect(screen, LIGHT_GRAY, volume_slider_rect)
            pygame.draw.rect(screen, DARK_GRAY, volume_slider_rect, 2)
            # CORRIGÉ: position du texte "désactivé" aussi ajustée
            disabled_text = small_font.render("Volume: Désactivé", True, DARK_GRAY)
            disabled_rect = disabled_text.get_rect(center=(center_x, volume_slider_rect.y + 45))
            screen.blit(disabled_text, disabled_rect)
        
        # Bouton test son
        test_color = BLUE if is_enabled else LIGHT_GRAY
        pygame.draw.rect(screen, test_color, test_button_rect)
        pygame.draw.rect(screen, BLACK, test_button_rect, 2)
        
        test_text = font.render("Tester le son", True, BLACK)
        test_text_rect = test_text.get_rect(center=test_button_rect.center)
        screen.blit(test_text, test_text_rect)
        
        # Bouton retour
        pygame.draw.rect(screen, RED, back_button_rect)
        pygame.draw.rect(screen, BLACK, back_button_rect, 2)
        
        back_text = font.render("Retour", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        screen.blit(back_text, back_text_rect)
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    mouse_x, mouse_y = event.pos
                    
                    # Toggle audio
                    if audio_toggle_rect.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')
                        audio_manager.toggle_audio()
                    
                    # Test son
                    elif test_button_rect.collidepoint(event.pos) and is_enabled:
                        audio_manager.play_sound('button_click')
                        audio_manager.play_sound('pawn_move')
                    
                    # Bouton retour
                    elif back_button_rect.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')
                        return
                    
                    # Slider de volume
                    elif (is_enabled and volume_slider_rect.collidepoint(event.pos)):
                        dragging_volume = True
                        update_volume_from_mouse(mouse_x)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_volume = False
            
            elif event.type == pygame.MOUSEMOTION:
                if dragging_volume and is_enabled:
                    mouse_x, mouse_y = event.pos
                    update_volume_from_mouse(mouse_x)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    audio_manager.play_sound('button_click')
                    return
        
        pygame.display.flip()
        clock.tick(60)