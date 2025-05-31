import json
import os
from datetime import datetime
from pathlib import Path

class SaveManager:
    def __init__(self):
        self.save_dir = Path("saves")
        self.save_file = self.save_dir / "game_save.json"
        self.ensure_save_directory()
    
    def ensure_save_directory(self):
        """Crée le dossier de sauvegarde s'il n'existe pas"""
        if not self.save_dir.exists():
            self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def save_game(self, game_state):
        """
        Sauvegarde l'état actuel du jeu
        
        Args:
            game_state (dict): Dictionnaire contenant toutes les informations de la partie
        """
        try:
            # Ajouter la date de sauvegarde
            game_state['save_date'] = datetime.now().isoformat()
            
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def load_game(self):
        """
        Charge une partie sauvegardée
        
        Returns:
            dict: État du jeu ou None si pas de sauvegarde
        """
        try:
            if not self.save_file.exists():
                return None
                
            with open(self.save_file, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
            
            return game_state
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return None
    
    def has_save(self):
        """Vérifie s'il existe une sauvegarde"""
        return self.save_file.exists()
    
    def delete_save(self):
        """Supprime la sauvegarde existante"""
        try:
            if self.save_file.exists():
                self.save_file.unlink()
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
            return False
    
    def get_save_info(self):
        """
        Récupère les informations sur la sauvegarde
        
        Returns:
            dict: Informations sur la sauvegarde ou None
        """
        if not self.has_save():
            return None
            
        try:
            game_state = self.load_game()
            if game_state:
                return {
                    'mode': game_state.get('game_mode', 'Inconnu'),
                    'current_player': game_state.get('current_player', 1),
                    'save_date': game_state.get('save_date', 'Date inconnue'),
                    'game_over': game_state.get('game_over', False)
                }
        except:
            return None
    
    def create_game_state(self, pawn_grid, board_grid, current_player, game_mode, 
                         selected_pawn=None, game_over=False, winner=0, 
                         connected_pawns=None, quadrants_data=None):
        """
        Crée un dictionnaire d'état de jeu pour la sauvegarde
        
        Args:
            pawn_grid: Grille des pions
            board_grid: Grille du plateau
            current_player: Joueur actuel
            game_mode: Mode de jeu
            selected_pawn: Pion sélectionné (optionnel)
            game_over: État de fin de partie
            winner: Gagnant de la partie
            connected_pawns: Pions connectés (pour Congress)
            quadrants_data: Données des quadrants
            
        Returns:
            dict: État du jeu formaté pour la sauvegarde
        """
        return {
            'pawn_grid': pawn_grid,
            'board_grid': board_grid,
            'current_player': current_player,
            'game_mode': game_mode,
            'selected_pawn': selected_pawn,
            'game_over': game_over,
            'winner': winner,
            'connected_pawns': connected_pawns or [],
            'quadrants_data': quadrants_data,
            'save_version': '1.0'
        }

# Instance globale du gestionnaire de sauvegarde
save_manager = SaveManager()