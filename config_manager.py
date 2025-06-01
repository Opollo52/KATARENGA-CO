import json
import sys
import pygame
from pathlib import Path

def read_config():
    """
    Lit le fichier de configuration et retourne un dictionnaire de paramètres
    """
    config = {
        "width": 800,
        "height": 500,
        "default_quadrants": [1, 2, 3, 4, 5, 6, 7, 8],
        "quadrants_folder": "quadrant",
        "use_images": True
    }
    
    try:
        
        if Path(__file__).name == "config_manager.py" and "quadrant" in str(Path(__file__).parent):
            # Si on est dans le dossier quadrant, remonter à la racine
            project_root = Path(__file__).parent.parent.absolute()
        else:
            # Si on est déjà à la racine
            project_root = Path(sys.argv[0]).parent.absolute()
            
        config_file = project_root / "config.txt"
        
        if config_file.exists():
            lines = config_file.read_text().splitlines()
            
            # Lecture des dimensions de base (premières lignes)
            if len(lines) >= 2:
                config["width"] = int(lines[0].strip())
                config["height"] = int(lines[1].strip())
            
            # Lecture des autres paramètres (format clé: valeur)
            for line in lines[2:]:  # Commencer après les dimensions
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == "default_quadrants":
                        # Convertir en entier
                        config["default_quadrants"] = list(range(1, int(value) + 1))
                    elif key == "quadrants_folder":
                        config["quadrants_folder"] = value
                    elif key == "use_images":
                        # Convertir string en boolean
                        config["use_images"] = value.lower() in ['true', '1', 'yes', 'on']
    except Exception as e:
        # En cas d'erreur, utiliser les valeurs par défaut
        print(f"Erreur lors de la lecture du config.txt: {e}")
        pass
    
    return config

def create_default_quadrants(config):
    """
    Crée les quadrants par défaut basés sur l'image
    """
    if Path(__file__).name == "config_manager.py" and "quadrant" in str(Path(__file__).parent):
        # Si on est dans le dossier quadrant, remonter à la racine
        project_root = Path(__file__).parent.parent.absolute()
    else:
        # Si on est déjà à la racine
        project_root = Path(sys.argv[0]).parent.absolute()
    
    json_path = project_root / "quadrant" / "quadrants.json"  # Dans le dossier quadrant
    quadrants_folder = project_root / "quadrant"              # Dossier quadrant pour les images
    assets_folder = project_root / "assets"                   # Dossier assets à la racine
    
    # Si le JSON existe déjà, on le charge
    if json_path.exists():
        try:
            quadrants_data = json.loads(json_path.read_text())
            
            # Si on a déjà des quadrants dans le JSON, on les retourne
            if quadrants_data:
                return quadrants_data
        except:
            quadrants_data = {}
    else:
        quadrants_data = {}
    
    # Créer le dossier des quadrants s'il n'existe pas
    quadrants_folder.mkdir(exist_ok=True)
    
    # Quadrants définis manuellement :  
    left_quadrants = [
        # Quadrant 1 
        [
            [1, 3, 2, 4],
            [4, 2, 1, 1],
            [2, 4, 3, 3],
            [3, 1, 4, 2]
        ],
        # Quadrant 3 
        [
            [2, 3, 1, 4],
            [4, 3, 1, 2],
            [1, 4, 2, 3],
            [3, 2, 4, 1]
        ],
        # Quadrant 5
        [
            [2, 3, 4, 1],
            [3, 2, 3, 4],
            [1, 4, 1, 2],
            [4, 2, 1, 3]
        ],
        # Quadrant 7 
        [
            [1, 3, 2, 4],
            [4, 3, 1, 1],
            [3, 2, 4, 2],
            [2, 4, 1, 3]
        ]
    ]
    
    # Générer les versions miroir 
    all_quadrants = []
    for q in left_quadrants:
        # Ajouter le quadrant original (gauche)
        all_quadrants.append(q)
        
        # Créer et ajouter la version miroir (droite)
        mirror = []
        for row in q:
            mirror.append(list(reversed(row)))
        all_quadrants.append(mirror)
    
    # Limiter le nombre de quadrants selon la configuration
    max_quadrants = len(config["default_quadrants"])
    all_quadrants = all_quadrants[:max_quadrants]
    
    # Générer les images des quadrants
    cell_size = 100  # Taille d'une cellule
    
    # Pygame setup
    pygame.init()
    
    images = {
        1: pygame.image.load(assets_folder / "img" / "yellow.png"),  
        2: pygame.image.load(assets_folder / "img" / "green.png"),   
        3: pygame.image.load(assets_folder / "img" / "blue.png"),    
        4: pygame.image.load(assets_folder / "img" / "red.png")      
    }
    
    # Redimensionner les images
    for key in images:
        images[key] = pygame.transform.scale(images[key], (cell_size, cell_size))
    
    # Utiliser la configuration pour déterminer si on utilise les images    
    use_images = config["use_images"]
    
    # Créer chaque quadrant
    for i, grid in enumerate(all_quadrants):
        quadrant_num = i + 1
        quadrant_id = f"quadrant_{quadrant_num}"
        
        img_filename = f"quadrant_{quadrant_num}.png"
        subfolder = quadrants_folder / "quadrant"
        subfolder.mkdir(exist_ok=True)  # Crée le sous-dossier s'il n'existe pas
        img_path = subfolder / img_filename

        
        # Créer l'image si elle n'existe pas
        if not img_path.exists():
            # Créer la surface
            surface = pygame.Surface((4 * cell_size, 4 * cell_size))
            surface.fill((255, 255, 255))
            
            # Dessiner la grille
            for row in range(4):
                for col in range(4):
                    cell_value = grid[row][col]
                    rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
                    
                    if use_images and cell_value in images:
                        # Utiliser l'image
                        surface.blit(images[cell_value], rect)
                    
                    # Ajouter une bordure
                    pygame.draw.rect(surface, (0, 0, 0), rect, 2)
            
            # Sauvegarder l'image
            pygame.image.save(surface, img_path)
        
        relative_path = f"quadrant/quadrant/{img_filename}"

        # Ajouter au dictionnaire de données
        quadrants_data[quadrant_id] = {
            "image_path": relative_path,  #  Chemin relatif 
            "grid": grid
        }
    
    # Sauvegarder le JSON dans le dossier quadrant
    try:
        json_path.write_text(json.dumps(quadrants_data, indent=4))
        print(f" Quadrants sauvegardés dans: {json_path}")
    except Exception as e:
        print(f" Erreur sauvegarde: {e}")
        pass
    
    return quadrants_data

def initialize_quadrants():
    """
    Initialise le système de quadrants
    """
    config = read_config()
    quadrants_data = create_default_quadrants(config)
    return config, quadrants_data
