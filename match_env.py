"""
match_env.py — Environnement Gymnasium pour l'entraînement PPO
Simule un match Eurobot 2026 SANS pygame (pas d'affichage).
Compatible Stable Baselines 3.

Comportement calqué exactement sur robot.py + obstacles.py du projet.

États internes du robot :
    IDLE        : aucun mouvement en cours          → -0.05 pts/s
    ROTATING    : en train de s'orienter            →  0
    MOVING      : déplacement en cours              →  selon action
    STUNNED     : recul après collision (→ IDLE)    → -0.5 ponctuel
    BLOCKED     : bloqué net (obstacle fixe)        → -10 pts/s

Espace d'état  : 21 variables normalisées [0, 1] 
Espace d'action: 14 actions discrètes 
"""

import math
import numpy as np
import gymnasium as gym
from gymnasium import spaces

# ── Constantes terrain ────────────────────────────────────────
TABLE_W = 3000
TABLE_H = 2000
MATCH_DURATION  = 100.0
DT              = 1 / 60
FRAMES_PAR_STEP = 300
COLLISION_DIST  = 600    

# ── Obstacle fixe ────────
OBS_X      = 600
OBS_Y      = 1600   
OBS_W      = 1800
OBS_H      = 400

# ── Objectifs & Points d'intérêt (en mm) ─────────────────────
# 9 Garde-mangers
GARDE_MANGERS = [
    (225,  350),  (225,  1150), (225,  1650),
    (1325, 450),  (1500, 1000), (1675, 450),
    (2775, 350),  (2775, 1150), (2775, 1650)
]

# 1 Nid allié (Zone de départ de l'équipe alliée)
NID_ALLIE = (300, 950)

# 3 Zones de Ramassage de noisettes au sol
ZONES_RAMASSAGE = [
    (900,  600),
    (1500, 1500),
    (2100, 600)
]

# Position du Thermomètre
THERMOMETRE_POS = (225, 50)

# Catalogue des actions
ACTIONS = (
    [("garde_manger", i) for i in range(9)]   # 0-8
    + [("nid",       0)]                       # 9
    + [("ramassage", i) for i in range(3)]     # 10-12
    + [("thermometre", 0)]                     # 13 
)
N_ACTIONS = len(ACTIONS)  # Égal à 14 

# Valeurs de récompense 
R_COLLECTING_ARRIVE = 5.0
R_RETURNING_ARRIVE  = 8.0
R_THERMOMETRE       = 10.0


# ── Classes Physiques Minimales ─────────
class MiniObstacleFixe:
    def distance_to(self, rx, ry):
        cx = max(OBS_X, min(rx, OBS_X + OBS_W))
        cy = max(OBS_Y, min(ry, OBS_Y + OBS_H))
        return math.hypot(rx - cx, ry - cy)

class MiniRobotSim:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle % 360

    def distance_to(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)


# ── Environnement Principal ──────────────────────────────────
class MatchEnv(gym.Env):
    metadata = {"render_modes": ["txt"]}

    def __init__(self):
        super().__init__()

        # Espace d'action discret (14 actions)
        self.action_space = spaces.Discrete(N_ACTIONS)

        # Espace d'observation : 21 dimensions 
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(21,), dtype=np.float32
        )

        self.obstacle = MiniObstacleFixe()
        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # Positions initiales (en mm)
        self.robot  = MiniRobotSim(300, 950, 0)
        self.ennemi = MiniRobotSim(2700, 950, 180)

        self._reset_state()
        return self._get_obs(), {}

    def _reset_state(self):
        self.step_count     = 0
        self.score          = 0.0
        self.zones_visitees = [False] * 9
        self.nid_atteint    = False
        self.thermo_pousse  = False   
        self._action_cible  = None
        self._action_kind   = None

    def step(self, action):
        self.step_count += 1

        # Détermination de la cible
        target = self._action_to_target(action)
        kind, idx = ACTIONS[action]

        # Simulation simple de déplacement instantané "téléportation ciblée"
        # mais on simule le fait qu'on arrive ou non
        arrived = True

        # Simulation de collision simple si on passe au travers du gros obstacle fixe
        if target is not None:
        # 1. Collision avec l'obstacle fixe 
            if self.obstacle.distance_to(target[0], target[1]) < 200:
                arrived = False
            # 2. Collision avec le robot ennemi
            elif self.robot.distance_to(self.ennemi) < COLLISION_DIST:
                arrived = False  # Le déplacement échoue 
            else:
                self.robot.x, self.robot.y = target[0], target[1]
                self.robot.angle = (self.robot.angle + 45) % 360 

        # Déplacement très basique et aléatoire de l'ennemi pour simuler de la vie
        self.ennemi.x += np.random.randint(-50, 51)
        self.ennemi.y += np.random.randint(-50, 51)
        self.ennemi.x = max(100, min(TABLE_W - 100, self.ennemi.x))
        self.ennemi.y = max(100, min(TABLE_H - 100, self.ennemi.y))

        # Calcul de la récompense avec punition de l'inactivité
        reward = self._calc_reward(action, arrived)

        # Condition de fin de match (100 secondes)
        # 1 step = 300 frames à 60 FPS = 5 secondes réelles. 100s / 5s = 20 steps par épisode.
        truncated = False
        terminated = (self.step_count >= 20)

        return self._get_obs(), reward, terminated, truncated, {}

    # ── Système de Récompenses (anti-triche et anti-statique) ───
    def _calc_reward(self, action, arrived):
        reward = 0.0
        kind, idx = ACTIONS[action]

        # 1. Pénalité de temps universelle par step 
        # Forcer l'IA à agir vite au lieu d'attendre et cumuler des micro-bonus passifs
        reward -= 0.5  

        # 2. Si le déplacement a échoué (collision / bloqué)
        if not arrived:
            return -5.0

        # 3. Pénalité de proximité avec l'ennemi (évitement de collision)
        if self.robot.distance_to(self.ennemi) < COLLISION_DIST:
            reward -= 2.0

        # 4. Attribution des récompenses lors de la réussite des tâches
        if kind == "garde_manger":
            if not self.zones_visitees[idx]:
                self.zones_visitees[idx] = True
                self.score += 3.0
                reward += R_COLLECTING_ARRIVE + 5.0  # Bonus pour l'encourager à bouger
            else:
                # Si elle y retourne alors qu'il est déjà vide, petite punition
                reward -= 0.2

        elif kind == "nid":
            if not self.nid_atteint:
                self.nid_atteint = True
                self.score += 10.0
                reward += R_RETURNING_ARRIVE + 10.0
            else:
                reward -= 0.2

        elif kind == "ramassage":
            self.score += 2.0
            reward += R_COLLECTING_ARRIVE

        elif kind == "thermometre":
            if not self.thermo_pousse:
                self.thermo_pousse = True
                self.score += 8.0              # Points du barème 
                reward += R_THERMOMETRE + 15.0 # Grosse récompense pour l'inciter à y aller
            else:
                reward -= 0.5                  # Punition s'il insiste sur un bouton déjà poussé

        return reward

    def _action_to_target(self, action):
        kind, idx = ACTIONS[action]
        if kind == "garde_manger": return GARDE_MANGERS[idx]
        if kind == "nid":          return NID_ALLIE
        if kind == "ramassage":    return ZONES_RAMASSAGE[idx]
        if kind == "thermometre":  return THERMOMETRE_POS
        return None

    # ── Observation (21 dimensions) ──────────────────────────
    def _get_obs(self):
        diag = math.hypot(TABLE_W, TABLE_H)
        dx   = self.robot.x - self.ennemi.x
        dy   = self.robot.y - self.ennemi.y
        dist_ennemi = math.hypot(dx, dy)
        dist_obs    = self.obstacle.distance_to(self.robot.x, self.robot.y)

        angle_vers_ennemi = math.degrees(math.atan2(dy, -dx)) % 360
        angle_rel = abs(((angle_vers_ennemi - self.robot.angle) + 180) % 360 - 180)

        temps_restant = max(0.0,
            MATCH_DURATION - self.step_count * DT * FRAMES_PAR_STEP)

        # Vecteur de base (11 éléments)
        base_obs = [
            self.robot.x     / TABLE_W,
            self.robot.y     / TABLE_H,
            self.robot.angle / 360.0,
            self.ennemi.x    / TABLE_W,
            self.ennemi.y    / TABLE_H,
            self.ennemi.angle / 360.0,
            min(1.0, dist_ennemi / diag),
            min(1.0, dist_obs / diag),
            angle_rel / 180.0,
            temps_restant / MATCH_DURATION,
            self.score / 50.0
        ]

        # États des garde-mangers (9 éléments)
        zones_obs = [1.0 if v else 0.0 for v in self.zones_visitees]

        # État du thermomètre (1 élément)
        thermo_obs = [1.0 if self.thermo_pousse else 0.0]

        # Total : 11 + 9 + 1 = 21 éléments
        return np.array(base_obs + zones_obs + thermo_obs, dtype=np.float32)

    def render(self, mode="txt"):
        if mode == "txt":
            print(f"Step {self.step_count} | Score: {self.score} | Pos: ({int(self.robot.x)}, {int(self.robot.y)})")