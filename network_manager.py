import socket
import threading
import json
import time

class NetworkManager:
    def __init__(self):
        self.socket = None
        self.is_server = False
        self.is_connected = False
        self.connection = None
        self.received_messages = []
        self.message_lock = threading.Lock()
        
    def start_server(self, port=12345):
        """Démarre le serveur pour attendre une connexion"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', port))
            self.socket.listen(1)
            self.is_server = True
            
            print(f"Serveur démarré sur le port {port}")
            print("En attente de connexion...")
            
            # Attendre une connexion (bloquant)
            self.connection, addr = self.socket.accept()
            self.is_connected = True
            print(f"Connexion établie avec {addr}")
            
            # Démarrer le thread de réception
            receive_thread = threading.Thread(target=self._receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Erreur lors du démarrage du serveur: {e}")
            return False
    
    def connect_to_server(self, host, port=12345):
        """Se connecte à un serveur"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connection = self.socket
            self.is_connected = True
            self.is_server = False
            
            print(f"Connecté au serveur {host}:{port}")
            
            # Démarrer le thread de réception
            receive_thread = threading.Thread(target=self._receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la connexion: {e}")
            return False
    
    def _receive_messages(self):
        """Thread pour recevoir les messages en continu"""
        while self.is_connected:
            try:
                data = self.connection.recv(1024)
                if not data:
                    break
                    
                message = data.decode('utf-8')
                with self.message_lock:
                    self.received_messages.append(json.loads(message))
                    
            except Exception as e:
                print(f"Erreur lors de la réception: {e}")
                break
        
        self.is_connected = False
    
    def send_message(self, message_type, data):
        """Envoie un message à l'autre joueur"""
        if not self.is_connected:
            return False
            
        try:
            message = {
                'type': message_type,
                'data': data,
                'timestamp': time.time()
            }
            
            json_message = json.dumps(message)
            self.connection.send(json_message.encode('utf-8'))
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi: {e}")
            return False
    
    def get_messages(self):
        """Récupère tous les messages reçus"""
        with self.message_lock:
            messages = self.received_messages.copy()
            self.received_messages.clear()
            return messages
    
    def disconnect(self):
        """Ferme la connexion"""
        self.is_connected = False
        if self.connection:
            self.connection.close()
        if self.socket:
            self.socket.close()
    
    def get_local_ip(self):
        """Obtient l'adresse IP locale"""
        try:
            # Crée une connexion temporaire pour obtenir l'IP locale
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_socket.connect(("8.8.8.8", 80))
            local_ip = temp_socket.getsockname()[0]
            temp_socket.close()
            return local_ip
        except:
            return "127.0.0.1"