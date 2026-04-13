import math
import pygame
from setup import TABLE_WIDTH_MM, TABLE_HEIGHT_MM, FIELD_HEIGHT, FIELD_WIDTH

# Robot specifications
ROBOT_WIDTH_MM  = 320
ROBOT_HEIGHT_MM = 290
init_x_mm   = 300
init_y_mm   = 950
init_angle  = 0

# Physique par défaut
max_speed_mm_s  = 1000
max_accel_mm_s2 = 2000
max_turning_speed = 500
max_turning_accel = 300

ROTATION_THRESHOLD = 1   # degrés
DISTANCE_THRESHOLD = 5   # mm
COLLISION_DISTANCE = 600 # mm — distance d'alerte/arrêt

FPS = 60

# ──────────────────────────────────────────────
#  États de la machine à états du robot
# ──────────────────────────────────────────────
IDLE      = "IDLE"
ROTATING  = "ROTATING"
MOVING    = "MOVING"
BLOCKED   = "BLOCKED"   # collision détectée, robot en attente
STUNNED = "STUNNED"


def create_robot_surface():
    px_width  = (ROBOT_WIDTH_MM  / TABLE_WIDTH_MM)  * FIELD_WIDTH
    px_height = (ROBOT_HEIGHT_MM / TABLE_HEIGHT_MM) * FIELD_HEIGHT
    px_x = ((TABLE_WIDTH_MM - init_x_mm) / TABLE_WIDTH_MM) * FIELD_WIDTH
    px_y = ((TABLE_HEIGHT_MM - init_y_mm) / TABLE_HEIGHT_MM) * FIELD_HEIGHT
    band_height = 8

    image_robot = pygame.Surface((px_width, px_height))
    image_robot.fill((0, 255, 0))
    image_robot.set_colorkey((0, 0, 0))
    pygame.draw.rect(image_robot, (0, 0, 255), (0, 0, px_width, band_height))
    rect_robot = image_robot.get_rect()
    rect_robot.center = (px_x, px_y)
    return image_robot, rect_robot


# ──────────────────────────────────────────────
#  Classe Graphique (inchangée)
# ──────────────────────────────────────────────
class Graphique:
    def __init__(self, robot, image_robot, screen, scaled_vinyle):
        self.robot = robot
        self.image_robot = image_robot
        self.screen = screen
        self.font   = pygame.font.Font(None, 18)
        self.chrono_font = pygame.font.Font(None, 24)
        self.scaled_vinyle = scaled_vinyle
        self.strategy_start_time    = 0
        self.strategy_elapsed_time  = 0

    def update_strategy_time(self, current_time, strategy_active):
        if strategy_active and self.strategy_start_time == 0:
            self.strategy_start_time = current_time
        elif strategy_active and self.strategy_start_time > 0:
            self.strategy_elapsed_time = current_time - self.strategy_start_time
        elif not strategy_active:
            self.strategy_start_time   = 0
            self.strategy_elapsed_time = 0

    def draw_background(self):
        """Dessine uniquement le fond (vinyle). À appeler UNE SEULE FOIS par frame."""
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(0, 0, FIELD_WIDTH, FIELD_HEIGHT))
        self.screen.blit(self.scaled_vinyle, (0, 0))

    def draw_robot(self):
        """Dessine uniquement ce robot par-dessus le fond déjà dessiné."""
        self.robot.angle_px = self.robot.conversion_trigo_transform_rotate(self.robot.angle)
        self.robot.px_x     = self.robot.conversion_From_mmx_To_px_x(self.robot.mm_x)
        self.robot.px_y     = self.robot.conversion_From_mmy_To_px_y(self.robot.mm_y)

        rotated_image = pygame.transform.rotate(self.image_robot, self.robot.angle_px)
        robot_rect    = rotated_image.get_rect(center=(self.robot.px_x, self.robot.px_y))
        self.screen.blit(rotated_image, robot_rect)

    def draw_hud(self):
        """Affiche coordonnées à gauche et chrono à droite du panneau, comme l'original."""
        state_color = (255, 100, 100) if self.robot.state == BLOCKED else (255, 255, 255)
        coords_text = self.font.render(
            f"X: {int(self.robot.mm_x)} mm, Y: {int(self.robot.mm_y)} mm, O: {int(self.robot.angle)}°  [{self.robot.state}]",
            True, state_color)
        self.screen.blit(coords_text, (910, 10))

        chrono_text  = self.chrono_font.render(f"{int(self.strategy_elapsed_time)}s", True, (255, 255, 0))
        chrono_width = chrono_text.get_width()
        self.screen.blit(chrono_text, (1200 - chrono_width - 10, 10))

    # Conservé pour compatibilité (ne redessine PAS le fond)
    def refesh_graphique(self):
        self.draw_robot()
        self.draw_hud()
        pygame.display.update()


# ──────────────────────────────────────────────
#  Classe Robot — machine à états non bloquante
# ──────────────────────────────────────────────
class Robot(Graphique):

    def __init__(self, scaled_vinyle=None, screen=None, image_robot=None,
                 x=init_x_mm, y=init_y_mm, angle=init_angle, speed=0):
        self.mm_x   = x
        self.mm_y   = y
        self.px_x   = ((TABLE_WIDTH_MM - x)  / TABLE_WIDTH_MM)  * FIELD_WIDTH
        self.px_y   = ((TABLE_HEIGHT_MM - y) / TABLE_HEIGHT_MM) * FIELD_HEIGHT
        self.angle  = angle
        self.angle_px = angle - 90

        self.old_x = x
        self.old_y = y
        
        # Physique
        self.speed              = speed
        self.max_speed          = max_speed_mm_s
        self.acceleration       = max_accel_mm_s2
        self.turning_speed      = 0
        self.max_turning_speed  = max_turning_speed
        self.turning_acceleration = max_turning_accel
        self.target_speed       = 0

        # Dimensions
        self.mm_width  = ROBOT_WIDTH_MM
        self.mm_height = ROBOT_HEIGHT_MM
        self.px_width  = (ROBOT_WIDTH_MM  / TABLE_WIDTH_MM)  * FIELD_WIDTH
        self.px_height = (ROBOT_HEIGHT_MM / TABLE_HEIGHT_MM) * FIELD_HEIGHT

        # ── Machine à états ──
        self.state = IDLE          # état courant
        self._blocked_timer = 0.0  # temps passé en BLOCKED

        # Cibles internes
        self._target_angle    = angle
        self._target_distance = 0.0
        self._face            = 0          # 0 = avant, 1 = arrière
        self._ratio_vitesse   = 100
        self._effective_speed = max_speed_mm_s  # vitesse corrigée par ratio

        # File de commandes (rejoindre = orienter puis avancer/reculer)
        self._command_queue = []   # liste de (fn, args)

        # Angles/distances utiles (public, lisibles de l'extérieur)
        self.angle_to_target       = angle
        self.angle_diff_to_target  = 0
        self.distance_to_target    = 0
        self.distance_x_to_target  = 0
        self.distance_y_to_target  = 0

        self._stun_retreat_mm   = 150   # distance de recul en mm
        self._stun_target_x     = None  # cible à reprendre après recul
        self._stun_target_y     = None

        # Graphique
        if image_robot and screen and scaled_vinyle:
            self.graphique = Graphique(self, image_robot, screen, scaled_vinyle)
        else:
            self.graphique = None
            print("erreur, missing arg: image ou screen")

    # ── Conversions coordonnées ─────────────────
    def conversion_From_mmx_To_px_x(self, mm_x):
        return ((TABLE_WIDTH_MM - mm_x) / TABLE_WIDTH_MM) * FIELD_WIDTH

    def conversion_From_mmy_To_px_y(self, mm_y):
        return ((TABLE_HEIGHT_MM - mm_y) / TABLE_HEIGHT_MM) * FIELD_HEIGHT

    def conversion_From_px_x_To_mm_x(self, px_x):
        return (FIELD_WIDTH - px_x) * (TABLE_WIDTH_MM / FIELD_WIDTH)

    def conversion_From_px_y_To_mmy(self, px_y):
        return (FIELD_HEIGHT - px_y) * (TABLE_HEIGHT_MM / FIELD_HEIGHT)

    def conversion_trigo_transform_rotate(self, angle):
        return angle - 90

    # ── Utilitaires angulaires ──────────────────
    def normalize_angle(self, angle):
        angle = angle % 360
        if angle > 180:
            angle -= 360
        return angle

    def calculate_target_angle(self, target_mm_x, target_mm_y):
        self.distance_x_to_target = self.mm_x - target_mm_x
        self.distance_y_to_target = target_mm_y - self.mm_y
        self.distance_to_target   = math.hypot(self.distance_x_to_target,
                                                self.distance_y_to_target)
        self.angle_to_target      = math.degrees(
            math.atan2(self.distance_y_to_target, self.distance_x_to_target))
        self.angle_diff_to_target = self.normalize_angle(
            self.angle_to_target - self.angle)
        return self.angle_to_target

    # ── Profils trapézoïdaux ────────────────────
    def _update_speed_trapezoidal(self, dt, distance_restante):
        v_max = self._effective_speed
        a     = self.acceleration
        d_accel = (v_max ** 2) / (2 * a)

        if distance_restante < 2 * d_accel:
            v_peak = min(math.sqrt(a * distance_restante), v_max)
        else:
            v_peak = v_max

        d_brake = (self.speed ** 2) / (2 * a)

        if self.speed < v_peak and distance_restante > d_brake:
            self.speed = min(self.speed + a * dt, v_peak)
        elif distance_restante <= d_brake and self.speed > 0:
            self.speed = max(self.speed - a * dt, 0)
        elif self.speed >= v_peak:
            self.speed = v_peak

        if distance_restante < DISTANCE_THRESHOLD:
            self.speed = 0

    def _update_turning_speed(self, dt, angle_diff_restante):
        w_max  = self.max_turning_speed
        alpha  = self.turning_acceleration
        w_peak = min(math.sqrt(2 * alpha * abs(angle_diff_restante)), w_max)

        d_brake_ang = (self.turning_speed ** 2) / (2 * alpha) if alpha > 0 else 0

        if self.turning_speed < w_peak and abs(angle_diff_restante) > d_brake_ang:
            self.turning_speed = min(self.turning_speed + alpha * dt, w_peak)
        elif abs(angle_diff_restante) <= d_brake_ang and self.turning_speed > 0:
            self.turning_speed = max(self.turning_speed - alpha * dt, 0)
        elif self.turning_speed >= w_peak:
            self.turning_speed = w_peak

        if abs(angle_diff_restante) < ROTATION_THRESHOLD:
            self.turning_speed = 0

    # ── Étapes de déplacement (une frame) ───────
    def _step_rotation(self, dt):
        """Tourne d'un pas vers _target_angle. Retourne True si terminé."""
        self.angle_diff_to_target = self.normalize_angle(
            self._target_angle - self.angle)
        self._update_turning_speed(dt, self.angle_diff_to_target)

        max_step = self.turning_speed * dt
        if abs(self.angle_diff_to_target) < ROTATION_THRESHOLD:
            self.angle = self._target_angle
            self.turning_speed = 0
            return True
        step = max_step if self.angle_diff_to_target > 0 else -max_step
        self.angle = self.normalize_angle(self.angle + step)
        return False

    def _step_translation(self, dt):
        """Avance/recule d'un pas. Retourne True si terminé."""
        self._update_speed_trapezoidal(dt, self._target_distance)
        radians = math.radians(self.angle)
        sign = -1 if self._face == 0 else 1  # face=0 avance, face=1 recule

        dx = sign * math.cos(radians) * self.speed * dt
        dy = -sign * math.sin(radians) * self.speed * dt
        step = math.hypot(dx, dy)

        if step >= self._target_distance:
            if step > 0:
                ratio = self._target_distance / step
                dx *= ratio
                dy *= ratio
            self._target_distance = 0
        else:
            self._target_distance -= step

        self.mm_x += dx
        self.mm_y += dy

        return self._target_distance <= DISTANCE_THRESHOLD

    # ── API publique : commandes non bloquantes ─
    def avancer(self, distance, ratio_vitesse):
        self._effective_speed = self.max_speed * (ratio_vitesse / 100)
        self._target_distance = float(distance)
        self._face            = 0
        self.speed            = 0
        self.state            = MOVING

    def reculer(self, distance, ratio_vitesse):
        self._effective_speed = self.max_speed * (ratio_vitesse / 100)
        self._target_distance = float(distance)
        self._face            = 1
        self.speed            = 0
        self.state            = MOVING

    def rebond(self, distance, ratio_vitesse):
        self._effective_speed = self.max_speed * (ratio_vitesse / 100)
        self._target_distance = float(distance)
        self._face            = 1
        self.speed            = 0
        self.state            = STUNNED

    def orienter(self, angle, ratio_vitesse):
        self._effective_speed = self.max_speed * (ratio_vitesse / 100)
        self._target_angle    = float(angle)
        self.turning_speed    = 0
        self.state            = ROTATING

    def cibler(self, target_mm_x, target_mm_y, ratio_vitesse):
        self.calculate_target_angle(target_mm_x, target_mm_y)
        self.orienter(self.angle_to_target, ratio_vitesse)

    def rejoindre(self, target_mm_x, target_mm_y, face, ratio_vitesse):
        """Enfile : orienter puis avancer/reculer."""
        self.calculate_target_angle(target_mm_x, target_mm_y)
        angle = self.angle_to_target
        if face == 1:
            angle = self.normalize_angle(angle + 180)
        dist = math.hypot(self.mm_x - target_mm_x, self.mm_y - target_mm_y)
        # On empile les deux sous-commandes
        self._command_queue = [
            ("orienter", (angle, ratio_vitesse)),
            ("avancer" if face == 0 else "reculer", (dist, ratio_vitesse)),
        ]
        # Démarre la première
        self._exec_next_command()

    def is_idle(self):
        return self.state == IDLE

    # ── Mise à jour par frame ───────────────────
    def update(self, dt, obstacles=None):
        """
        Appeler une fois par frame depuis la boucle principale.
        obstacles : liste de Robot (ou objets avec .mm_x, .mm_y) à éviter.
        """
        # ── Détection de collision ─────────────────
        if obstacles:
            closest = self._closest_obstacle(obstacles)
            if closest is not None and closest < COLLISION_DISTANCE:
                if self.state == MOVING:
                    self._start_stun()
            else:
                pass

        # ── Exécution de l'état courant ────────────
        if self.state == IDLE:
            return

        if self.state == BLOCKED:
            self._blocked_timer += dt
            self.speed = 0
            return

        if self.state == ROTATING:
            done = self._step_rotation(dt)
            if done:
                self._exec_next_command()

        if self.state == STUNNED:
            done = self._step_translation(dt)
            if done:
                self.speed = 0
                self.state = IDLE  

        elif self.state == MOVING:
            done = self._step_translation(dt)
            if done:
                self.speed = 0
                self._exec_next_command()

    def _exec_next_command(self):
        """Exécute la prochaine commande dans la file, ou passe à IDLE."""
        if self._command_queue:
            fn_name, args = self._command_queue.pop(0)
            getattr(self, fn_name)(*args)
        else:
            self.state = IDLE

    def _closest_obstacle(self, obstacles):
        """Retourne la distance au plus proche obstacle, ou None."""
        min_dist = None
        for obs in obstacles:
            if hasattr(obs, 'distance_to_robot'):
                d = obs.distance_to_robot(self.mm_x, self.mm_y)
            else:
                # Robot ennemi : distance centre à centre
                d = math.hypot(self.mm_x - obs.mm_x, self.mm_y - obs.mm_y)
            if min_dist is None or d < min_dist:
                min_dist = d
        return min_dist
    
    def _start_stun(self):
        if self._command_queue:
            # La dernière commande de la file est l'avancer/reculer vers la cible
            self._stun_target_x = None  # sera recalculé via rejoindre si besoin
            self._stun_target_y = None
        self._command_queue = []
        # Recule sur la direction opposée à l'angle actuel
        self._face = 1   # forcer le recul
        self._target_distance = self._stun_retreat_mm
        self.speed = 0
        self.state = STUNNED

    def adapter_vitesse(self, ennemi, angle_vision=120, distance_securite=1000):
        """
        Adapte la vitesse EN TEMPS RÉEL selon la position de l'ennemi.
        Agit sur _effective_speed, lu à chaque frame par _update_speed_trapezoidal.

        angle_vision      : largeur du cône de danger devant le robot (degrés)
        distance_securite : distance de référence pour les paliers (mm)
        """
        dx = ennemi.mm_x - self.mm_x
        dy = ennemi.mm_y - self.mm_y
        distance = math.hypot(dx, dy)

        # Angle de l'ennemi dans le repère du terrain, puis relatif à l'orientation du robot
        angle_vers_ennemi = math.degrees(math.atan2(dy, -dx))
        angle_relatif = abs(self.normalize_angle(angle_vers_ennemi - self.angle))
        # angle_relatif = 0°   → ennemi pile devant
        # angle_relatif = 180° → ennemi pile derrière

        dans_cone_danger = angle_relatif < (angle_vision / 2)

        # Paliers discrets — légers pour la Raspberry
        if dans_cone_danger:
            if distance < distance_securite:    # < 1000mm : 50%
                self._effective_speed = max_speed_mm_s * 0.5
        else:
            self._effective_speed = max_speed_mm_s       # voie libre : vitesse max

        return distance, angle_relatif, dans_cone_danger


# ──────────────────────────────────────────────
#  Robot ennemi avec patrouille
# ──────────────────────────────────────────────
class RobotEnnemi(Robot):
    """
    Robot ennemi autonome qui patrouille entre une liste de waypoints.
    Il utilise la même machine à états que Robot.
    """
    def __init__(self, scaled_vinyle, screen, image_robot,
                 waypoints=None, patrol_speed=80):
        super().__init__(scaled_vinyle, screen, image_robot,
                         x=2500, y=1000, angle=180)
        self._waypoints    = waypoints or [
            (2500, 300),
            (2500, 1700),
            (500,  1700),
            (500,  300),
        ]
        self._wp_index      = 0
        self._patrol_speed  = patrol_speed
        self._go_to_next_wp()

    def _go_to_next_wp(self):
        tx, ty = self._waypoints[self._wp_index]
        self.rejoindre(tx, ty, face=0, ratio_vitesse=self._patrol_speed)

    def update(self, dt, obstacles=None):
        """Met à jour la patrouille : quand IDLE, passe au waypoint suivant."""
        if obstacles:
            closest = self._closest_obstacle(obstacles)
            if closest is not None and closest < COLLISION_DISTANCE:
                if self.state == MOVING:
                    self._start_stun()
            else:
                pass


        # ── Exécution de l'état courant ────────────
        if self.state == IDLE:
            self._wp_index = (self._wp_index + 1) % len(self._waypoints)
            self._go_to_next_wp()

        if self.state == BLOCKED:
            self._blocked_timer += dt
            self.speed = 0
            return

        if self.state == ROTATING:
            done = self._step_rotation(dt)
            if done:
                self._exec_next_command()

        if self.state == STUNNED:
            done = self._step_translation(dt)
            if done:
                self.speed = 0
                self.state = IDLE 

        elif self.state == MOVING:
            done = self._step_translation(dt)
            if done:
                self.speed = 0
                self._exec_next_command()

        
        