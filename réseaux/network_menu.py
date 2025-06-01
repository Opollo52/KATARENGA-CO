import pygame
import sys
import threading
from pathlib import Path
from assets.colors import Colors
from assets.audio_manager import audio_manager  # IMPORT AUDIO
from réseaux.network_manager import NetworkManager

def show_network_menu(screen):
    """
    Affiche le menu de connexion réseau
    """
    WIDTH, HEIGHT = screen.get_width(), screen.get_height()
    pygame.display.set_caption("Jeu en réseau")
    
    # Couleurs et ressources
    script_dir = Path(__file__).parent.parent.absolute()
    background_image = pygame.image.load(str(script_dir / "assets" / "img" / "fond.png"))
    
    WHITE = Colors.WHITE
    BLACK = Colors.BLACK
    BLUE = Colors.BLUE
    RED = Colors.RED
    GREEN = Colors.GREEN
    LIGHT_GRAY = Colors.LIGHT_GRAY
    
    # Polices
    title_font = pygame.font.Font(None, 42)
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    # État de l'interface
    mode = "menu"  # "menu", "host", "join", "connecting", "connected"
    network_manager = NetworkManager()
    input_text = ""
    input_active = False
    status_message = ""
    connection_thread = None
    
    # Configuration des boutons
    button_width = 300
    button_height = 60
    button_spacing = 20
    
    # Centrage vertical
    total_height = (button_height * 3) + (button_spacing * 2)
    start_y = (HEIGHT - total_height) // 2
    
    # Boutons du menu principal
    host_button = pygame.Rect((WIDTH - button_width) // 2, start_y, button_width, button_height)
    join_button = pygame.Rect((WIDTH - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height)
    back_button = pygame.Rect((WIDTH - button_width) // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height)
    
    # Zone de saisie IP
    input_box = pygame.Rect((WIDTH - 300) // 2, HEIGHT // 2, 300, 40)
    connect_button = pygame.Rect((WIDTH - 200) // 2, HEIGHT // 2 + 60, 200, 50)
    cancel_button = pygame.Rect((WIDTH - 200) // 2, HEIGHT // 2 + 120, 200, 50)
    
    def draw_centered_text(text, rect, color, font_obj=font):
        """Dessine un texte centré dans un rectangle"""
        text_surf = font_obj.render(text, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
    
    def start_server_thread():
        """Lance le serveur dans un thread séparé"""
        nonlocal status_message, mode
        if network_manager.start_server():
            status_message = "Connexion établie !"
            mode = "connected"
        else:
            status_message = "Erreur lors du démarrage du serveur"
            mode = "menu"
    
    def connect_to_server_thread(host_ip):
        """Se connecte au serveur dans un thread séparé"""
        nonlocal status_message, mode
        if network_manager.connect_to_server(host_ip):
            status_message = "Connexion établie !"
            mode = "connected"
        else:
            status_message = "Impossible de se connecter"
            mode = "menu"
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Affichage du fond
        background_scaled = pygame.transform.scale(background_image, screen.get_size())
        screen.blit(background_scaled, (0, 0))
        
        # Menu principal
        if mode == "menu":
            # Titre
            title = title_font.render("Jeu en Réseau", True, BLACK)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
            
            # Fond semi-transparent pour le titre
            bg_surface = pygame.Surface((title_rect.width + 20, title_rect.height + 10), pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 180))
            screen.blit(bg_surface, (title_rect.x - 10, title_rect.y - 5))
            screen.blit(title, title_rect)
            
            # Boutons
            pygame.draw.rect(screen, BLUE, host_button)
            pygame.draw.rect(screen, GREEN, join_button)
            pygame.draw.rect(screen, RED, back_button)
            
            draw_centered_text("Héberger une partie", host_button, BLACK)
            draw_centered_text("Rejoindre une partie", join_button, BLACK)
            draw_centered_text("Retour", back_button, BLACK)
            
            # Afficher l'IP locale pour information
            local_ip = network_manager.get_local_ip()
            ip_text = small_font.render(f"Votre IP : {local_ip}", True, BLACK)
            ip_rect = ip_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            
            bg_surface = pygame.Surface((ip_rect.width + 16, ip_rect.height + 8), pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 120))
            screen.blit(bg_surface, (ip_rect.x - 8, ip_rect.y - 4))
            screen.blit(ip_text, ip_rect)
            
            # Message de statut s'il y en a un
            if status_message:
                status_text = font.render(status_message, True, RED)
                status_rect = status_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
                
                bg_surface = pygame.Surface((status_rect.width + 16, status_rect.height + 8), pygame.SRCALPHA)
                bg_surface.fill((255, 255, 255, 120))
                screen.blit(bg_surface, (status_rect.x - 8, status_rect.y - 4))
                screen.blit(status_text, status_rect)
        
        # Mode hébergement
        elif mode == "host":
            title = title_font.render("Hébergement de partie", True, BLACK)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            
            bg_surface = pygame.Surface((title_rect.width + 20, title_rect.height + 10), pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 180))
            screen.blit(bg_surface, (title_rect.x - 10, title_rect.y - 5))
            screen.blit(title, title_rect)
            
            info_text = font.render("En attente de connexion...", True, BLACK)
            info_rect = info_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            bg_surface = pygame.Surface((info_rect.width + 16, info_rect.height + 8), pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 120))
            screen.blit(bg_surface, (info_rect.x - 8, info_rect.y - 4))
            screen.blit(info_text, info_rect)
            
            # Afficher l'IP
            local_ip = network_manager.get_local_ip()
            ip_info = small_font.render(f"Communiquez cette IP à votre adversaire : {local_ip}", True, BLACK)
            ip_rect = ip_info.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            
            bg_surface = pygame.Surface((ip_rect.width + 16, ip_rect.height + 8), pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 120))
            screen.blit(bg_surface, (ip_rect.x - 8, ip_rect.y - 4))
            screen.blit(ip_info, ip_rect)
            
            # Bouton annuler
            pygame.draw.rect(screen, RED, cancel_button)
            draw_centered_text("Annuler", cancel_button, BLACK)
        
        # Mode connexion
        elif mode == "join":
            title = title_font.render("Rejoindre une partie", True, BLACK)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            
            bg_surface = pygame.Surface((title_rect.width + 20, title_rect.height + 10), pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 180))
            screen.blit(bg_surface, (title_rect.x - 10, title_rect.y - 5))
            screen.blit(title, title_rect)
            
            # Zone de saisie IP
            input_color = BLUE if input_active else LIGHT_GRAY
            pygame.draw.rect(screen, WHITE, input_box)
            pygame.draw.rect(screen, input_color, input_box, 2)
            
            # Texte de saisie
            if input_text:
                text_surface = font.render(input_text, True, BLACK)
                screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
            else:
                placeholder = small_font.render("Saisissez l'IP du serveur", True, (128, 128, 128))
                screen.blit(placeholder, (input_box.x + 5, input_box.y + 10))
            
            # Boutons
            pygame.draw.rect(screen, GREEN, connect_button)
            pygame.draw.rect(screen, RED, cancel_button)
            
            draw_centered_text("Se connecter", connect_button, BLACK)
            draw_centered_text("Annuler", cancel_button, BLACK)
        
        # Mode connexion en cours
        elif mode == "connecting":
            title = title_font.render("Connexion en cours...", True, BLACK)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            bg_surface = pygame.Surface((title_rect.width + 20, title_rect.height + 10), pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 180))
            screen.blit(bg_surface, (title_rect.x - 10, title_rect.y - 5))
            screen.blit(title, title_rect)
        
        # Mode connecté
        elif mode == "connected":
            title = title_font.render("Connexion établie !", True, GREEN)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            
            bg_surface = pygame.Surface((title_rect.width + 20, title_rect.height + 10), pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 180))
            screen.blit(bg_surface, (title_rect.x - 10, title_rect.y - 5))
            screen.blit(title, title_rect)
            
            info = font.render("Prêt à jouer !", True, BLACK)
            info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            bg_surface = pygame.Surface((info_rect.width + 16, info_rect.height + 8), pygame.SRCALPHA)
            bg_surface.fill((255, 255, 255, 120))
            screen.blit(bg_surface, (info_rect.x - 8, info_rect.y - 4))
            screen.blit(info, info_rect)
            
            # Bouton pour lancer le jeu
            start_game_button = pygame.Rect((WIDTH - 200) // 2, HEIGHT // 2 + 50, 200, 50)
            pygame.draw.rect(screen, BLUE, start_game_button)
            draw_centered_text("Commencer", start_game_button, BLACK)
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                network_manager.disconnect()
                return
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mode == "menu":
                    if host_button.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')  #   gestion SON
                        mode = "host"
                        status_message = ""
                        connection_thread = threading.Thread(target=start_server_thread)
                        connection_thread.daemon = True
                        connection_thread.start()
                    
                    elif join_button.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')  #   gestion SON
                        mode = "join"
                        status_message = ""
                        input_text = ""
                    
                    elif back_button.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')  #   gestion SON
                        network_manager.disconnect()
                        return
                
                elif mode == "join":
                    if input_box.collidepoint(event.pos):
                        input_active = True
                    else:
                        input_active = False
                    
                    if connect_button.collidepoint(event.pos) and input_text.strip():
                        audio_manager.play_sound('button_click')  #   gestion SON
                        mode = "connecting"
                        connection_thread = threading.Thread(target=connect_to_server_thread, args=(input_text.strip(),))
                        connection_thread.daemon = True
                        connection_thread.start()
                    
                    elif cancel_button.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')  #   gestion SON
                        mode = "menu"
                        input_text = ""
                        input_active = False
                
                elif mode == "host":
                    if cancel_button.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')  #  gestion SON
                        network_manager.disconnect()
                        mode = "menu"
                
                elif mode == "connected":
                    if start_game_button.collidepoint(event.pos):
                        audio_manager.play_sound('button_click')  #   gestion SON
                        # Lancer le jeu en réseau
                        from réseaux.network_game import start_network_game
                        start_network_game(screen, network_manager)
                        # Après le jeu, revenir au menu
                        mode = "menu"
                        network_manager.disconnect()
                        network_manager = NetworkManager()
            
            elif event.type == pygame.KEYDOWN and mode == "join" and input_active:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN and input_text.strip():
                    audio_manager.play_sound('button_click')  #   gestion SON
                    mode = "connecting"
                    connection_thread = threading.Thread(target=connect_to_server_thread, args=(input_text.strip(),))
                    connection_thread.daemon = True
                    connection_thread.start()
                else:
                    # Limiter la longueur et accepter seulement les caractères valides pour une IP
                    if len(input_text) < 15 and (event.unicode.isdigit() or event.unicode == '.'):
                        input_text += event.unicode
        
        pygame.display.flip()
        clock.tick(60)
    
    network_manager.disconnect()
