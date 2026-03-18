import os
import pygame

def ensure_strategie_directory():
    """Crée le dossier strategie_txt s'il n'existe pas"""
    directory = "strategie_txt"
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Dossier {directory} créé")
    return directory

def create_txt_file(filename):
    if not filename.endswith('.txt'):
        filename += '.txt'
    
    # S'assurer que le dossier existe
    directory = ensure_strategie_directory()
    
    # Créer le chemin complet
    full_path = os.path.join(directory, filename)
    
    with open(full_path, 'w') as f:
        pass  # Crée un fichier vide
    
    print(f"Fichier créé: {full_path}")
    return full_path

def convert_angle_from_simulation_to_robot(angle):
    """ l'emplacement du 0 degrés et du sens de rotation ne sont 
    pas les meme entre la simulations et la robot
    pour résoudre ce problème on modifie la valeur de l'angle pour quel
    corresponde au cercle trigonométrique."""
    """
    Simulation --> Robot
    0 --> 180
    90 --> 90
    180 --> 0
    190 --> 350
    270 --> 270
    340 (340-180)=160 --> 360-160
    """
    if angle <=180:
        angle = 180 - angle
    else:
        angle = 360 - (angle - 180) 
    return angle 



def write_rejoindre_command(target_mm_x, target_mm_y, filename, face="0", ratio_vitesse="100", ser="ser"):

    if target_mm_x < 0 :
        return None

    # S'assurer que le dossier existe et obtenir le chemin complet
    directory = ensure_strategie_directory()
    if not os.path.dirname(filename):  # Si pas de dossier dans le nom de fichier
        filename = os.path.join(directory, filename)

    # Formatage des coordonnées sur 4 chiffres avec des zéros devant
    x_str = f"{int(target_mm_x):04d}"
    y_str = f"{int(target_mm_y):04d}"
    # Construction de la ligne au format attendu
    line = f'fdd.rejoindre("{x_str}", "{y_str}", "{face}", "{ratio_vitesse}", {ser})\n'
    # Écriture dans le fichier
    with open(filename, 'a') as f:
        f.write(line)

def write_orienter_command(robot_angle, filename, ratio_vitesse="100", ser="ser"):
    # S'assurer que le dossier existe et obtenir le chemin complet
    directory = ensure_strategie_directory()
    if not os.path.dirname(filename):  # Si pas de dossier dans le nom de fichier
        filename = os.path.join(directory, filename)
        
    # Convertir l'angle de simulation vers robot
    robot_angle_converted = convert_angle_from_simulation_to_robot(robot_angle)
    # Formatage de l'angle sur 3 chiffres avec des zéros devant
    angle_str = f"{int(robot_angle_converted):03d}"
    # Construction de la ligne au format attendu
    line = f'fdd.orienter("{angle_str}", "{ratio_vitesse}", {ser})\n'
    # Écriture dans le fichier
    with open(filename, 'a') as f:
        f.write(line)

def display_mouse_coords(screen, mouse_mm_x, mouse_mm_y, Screen_HEIGHT, font_size=15, color=(255, 255, 0)):
    font = pygame.font.Font(None, font_size)
    mouse_text = font.render(f"Souris terrain: X={mouse_mm_x} mm, Y={mouse_mm_y} mm", True, color)
    screen.blit(mouse_text, (910, Screen_HEIGHT - 30))

