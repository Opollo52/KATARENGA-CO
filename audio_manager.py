import pygame
import json
from pathlib import Path

class AudioManager:
    def __init__(self):
        self.sounds = {}
        self.settings = self.load_settings()
        self.init_pygame_mixer()
        self.load_sounds()
    
    def init_pygame_mixer(self):
        """Initialise le système audio de pygame"""
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("✅ Système audio initialisé")
        except pygame.error as e:
            print(f"❌ Erreur audio: {e}")
    
    def load_settings(self):
        """Charge les paramètres audio depuis settings.json"""
        try:
            project_root = Path(__file__).parent.parent.absolute()
            settings_file = project_root / "assets" / "settings.json"
            
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('audio', {'enabled': True, 'volume': 0.7})
            else:
                # Créer le fichier de settings par défaut
                default_settings = {
                    'audio': {
                        'enabled': True,
                        'volume': 0.7
                    }
                }
                settings_file.parent.mkdir(exist_ok=True)
                with open(settings_file, 'w') as f:
                    json.dump(default_settings, f, indent=4)
                return default_settings['audio']
                
        except Exception as e:
            print(f"Erreur chargement settings: {e}")
            return {'enabled': True, 'volume': 0.7}
    
    def save_settings(self):
        """Sauvegarde les paramètres audio"""
        try:
            project_root = Path(__file__).parent.parent.absolute()
            settings_file = project_root / "assets" / "settings.json"
            
            # Charger les settings existants ou créer nouveaux
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            else:
                settings = {}
            
            # Mettre à jour la section audio
            settings['audio'] = self.settings
            
            # Sauvegarder
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
                
        except Exception as e:
            print(f"Erreur sauvegarde settings: {e}")
    
    def load_sounds(self):
        """Charge tous les fichiers audio"""
        try:
            project_root = Path(__file__).parent.parent.absolute()
            sound_folder = project_root / "assets" / "sound"
            
            # Définir les sons attendus (avec support MP3 et WAV)
            sound_files = {
                'button_click': ['button_click.wav', 'button_click.mp3'],
                'pawn_move': ['pawn_move.wav', 'pawn_move.mp3']
            }
            
            for sound_name, possible_files in sound_files.items():
                sound_loaded = False
                for filename in possible_files:
                    sound_path = sound_folder / filename
                    if sound_path.exists():
                        try:
                            self.sounds[sound_name] = pygame.mixer.Sound(str(sound_path))
                            self.sounds[sound_name].set_volume(self.settings['volume'])
                            print(f"✅ Son chargé: {sound_name} ({filename})")
                            sound_loaded = True
                            break
                        except pygame.error as e:
                            print(f"❌ Erreur chargement {filename}: {e}")
                
                if not sound_loaded:
                    print(f"⚠️  Aucun fichier trouvé pour: {sound_name}")
                    print(f"    Fichiers recherchés: {possible_files}")
                    
        except Exception as e:
            print(f"Erreur chargement sons: {e}")
    
    def play_sound(self, sound_name):
        """Joue un son si audio activé"""
        if not self.settings['enabled']:
            return
            
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except pygame.error as e:
                print(f"Erreur lecture {sound_name}: {e}")
    
    def set_volume(self, volume):
        """Définit le volume (0.0 à 1.0)"""
        self.settings['volume'] = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.settings['volume'])
        self.save_settings()
    
    def toggle_audio(self):
        """Active/désactive l'audio"""
        self.settings['enabled'] = not self.settings['enabled']
        self.save_settings()
        return self.settings['enabled']
    
    def is_enabled(self):
        """Retourne si l'audio est activé"""
        return self.settings['enabled']

# Instance globale du gestionnaire audio
audio_manager = AudioManager()