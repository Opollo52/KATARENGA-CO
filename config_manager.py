import json
import os
import sys
import pygame

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
        with open("config.txt", "r") as f:
            lines = f.readlines()
            
        # Lecture des dimensions de base
        if len(lines) >= 2:
            config["width"] = int(lines[0].strip())
            config["height"] = int(lines[1].strip())
    except:
        # En cas d'erreur, utiliser les valeurs par défaut
        pass
    
    return config

def create_default_quadrants(config):
    """
    Crée les quadrants par défaut basés sur l'image
    """
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    json_path = os.path.join(script_dir, "quadrants.json")
    quadrants_folder = os.path.join(script_dir, config["quadrants_folder"])
    
    # Si le JSON existe déjà, on le charge
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                quadrants_data = json.load(f)
            
            # Si on a déjà des quadrants dans le JSON, on les retourne
            if quadrants_data:
                return quadrants_data
        except:
            quadrants_data = {}
    else:
        quadrants_data = {}
    
    # Créer le dossier des quadrants s'il n'existe pas
    os.makedirs(quadrants_folder, exist_ok=True)
    
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
    
    # Générer les images des quadrants
    cell_size = 100  # Taille d'une cellule
    
    # Pygame setup
    pygame.init()
    
    # Charger les images 
    images = {
        1: pygame.image.load(os.path.join(script_dir, "assets", "img", "yellow.png")),  
        2: pygame.image.load(os.path.join(script_dir, "assets", "img", "green.png")),   
        3: pygame.image.load(os.path.join(script_dir, "assets", "img", "blue.png")),    
        4: pygame.image.load(os.path.join(script_dir, "assets", "img", "red.png"))      
    }
    
    # Redimensionner les images
    for key in images:
        images[key] = pygame.transform.scale(images[key], (cell_size, cell_size))
    
        
    use_images = True
    
    # Créer chaque quadrant
    for i, grid in enumerate(all_quadrants):
        quadrant_num = i + 1
        quadrant_id = f"quadrant_{quadrant_num}"
        
        # Chemin de l'image
        img_filename = f"quadrant_{quadrant_num}.png"
        img_path = os.path.join(quadrants_folder, img_filename)
        
        # Créer l'image si elle n'existe pas
        if not os.path.exists(img_path):
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
        
        # Ajouter au dictionnaire de données
        quadrants_data[quadrant_id] = {
            "image_path": os.path.abspath(img_path),
            "grid": grid
        }
    
    # Sauvegarder le JSON
    try:
        with open(json_path, "w") as f:
            json.dump(quadrants_data, f, indent=4)
    except:
        pass
    
    return quadrants_data

def initialize_quadrants():
    """
    Initialise le système de quadrants
    """
    config = read_config()
    quadrants_data = create_default_quadrants(config)
    return config, quadrants_data