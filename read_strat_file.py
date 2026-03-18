import re
import os

def parse_fdd_commands(file_path):
    fdd_commands = []
    
    # Vérifier si le fichier existe dans le dossier strategie_txt
    if not os.path.exists(file_path):
        # Essayer dans le dossier strategie_txt
        strategie_path = os.path.join("strategie_txt", file_path)
        if os.path.exists(strategie_path):
            file_path = strategie_path
        else:
            raise FileNotFoundError(f"Fichier de stratégie non trouvé: {file_path}")
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("fdd."):
                # Extraire le nom de la fonction et les arguments
                match = re.match(r"fdd\.(\w+)\((.*)\)", line)
                if match:
                    function_name = match.group(1)  # Nom de la fonction
                    raw_args = match.group(2)      # Arguments bruts
                    # Convertir les arguments en liste, en enlevant les guillemets et espaces
                    args = [arg.strip().strip('"') for arg in raw_args.split(",")]
                    fdd_commands.append((function_name, args))
    return fdd_commands

## function inutile surement utilser pour des test
def execute_fdd_commands(commands, robot_instance):
    for function_name, args in commands:
        if function_name == "avancer":
            # Convertir les arguments en types corrects
            distance = int(args[0])
            ration_vitesse = int(args[1])
            # Appeler la méthode correspondante
            robot_instance.avancer(distance, ration_vitesse, 0.030)  # Ratio de vitesse 1.0, dt fictif
        elif function_name == "cibler":
            # Exemple pour une autre fonction
            print(f"Appel de la fonction cibler avec les arguments : {args}")
        else:
            print(f"Fonction {function_name} non reconnue ou non prise en charge.")


def convert_angle_from_robot_to_simulation(angle):
    """ l'emplacement du 0 degrés et du sens de rotation ne sont 
    pas les meme entre la simulations et la robot
    pour résoudre ce problème on modifie la valeur de l'angle pour quel
    corresponde au cercle trigonométrique."""

    """
    Robot --> simulation
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

 

def strategie(robot, flag_start=False, commands=None):

    if not flag_start:
        return None

    if commands :
        function_name, args = commands[0]  # Récupérer la première commande
        if function_name == "avancer":
            # Convertir les arguments en types corrects
            distance = int(args[0])
            ratio_vitesse = int(args[1])
            print("distance_avancer: ", distance, "  ratio_vitesse: ", ratio_vitesse)
            robot.avancer(distance, ratio_vitesse)
        elif function_name == "reculer":
            distance = int(args[0])
            ratio_vitesse = int(args[1])
            print("distance_reculer: ", distance, "  ratio_vitesse: ", ratio_vitesse)
            robot.reculer(distance, ratio_vitesse)

        elif function_name == "orienter":
            angle = int(args[0])
            angle = convert_angle_from_robot_to_simulation(angle)
            ratio_vitesse = int(args[1])
            robot.orienter(angle, ratio_vitesse)
            print("angle: ", angle, "  ratio_vitesse: ", ratio_vitesse)

        elif function_name == "cibler":
            target_mm_x = int(args[0])
            target_mm_y = int(args[1])
            ratio_vitesse = int(args[2])
            robot.cibler(target_mm_x, target_mm_y, ratio_vitesse)
            print("target_mm_x: ", target_mm_x, "  target_mm_y: ", target_mm_y, "  ratio_vitesse: ", ratio_vitesse)

        elif function_name == "rejoindre":
            target_mm_x = int(args[0])
            target_mm_y = int(args[1])
            face = int(args[2])
            ratio_vitesse = int(args[3])
            robot.rejoindre(target_mm_x, target_mm_y,face, ratio_vitesse)
            print("target_mm_x: ", target_mm_x, "  target_mm_y: ", target_mm_y, "  face: ", face, "  ratio_vitesse: ", ratio_vitesse)
        else:
            print(f"Fonction {function_name} non reconnue ou non prise en charge.")
        
        commands.pop(0)

