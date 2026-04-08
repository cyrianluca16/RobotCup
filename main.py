import pygame
import pygame_gui
import math

from side_bare import create_sidebar, parse_number, UI_W
from robot import Robot, RobotEnnemi, FPS, COLLISION_DISTANCE, IDLE, create_robot_surface
from setup import init, Screen_WIDTH, Screen_HEIGHT, FIELD_WIDTH, FIELD_HEIGHT
from read_strat_file import strategie, parse_fdd_commands
from rec_strat import (write_rejoindre_command, write_orienter_command,
                       create_txt_file, display_mouse_coords)

# ── Chemins par défaut ──────────────────────────────────────
file_strat_path = 'test.txt'
file_rec_path   = 'rec.txt'

# ── État global de l'UI ─────────────────────────────────────
face_robot     = 0
vitesse_robot  = 100
fonction_robot = "rejoindre"
enregistrement = False
commands        = None
start_strat     = False
stop_strat      = False
pause_strat     = False
running         = True
strategy_start_time = 0
mouse_mm_x_valid, mouse_mm_y_valid = 0, 0
last_rec_path = None  # garde le chemin du dernier fichier enregistré

# ── Timer de match ───────────────────────────────────────────
MATCH_DURATION   = 100.0   # secondes
match_running    = False
match_start_time = 0.0
match_end_freeze = False   # True pendant les 3s de gel post-match
match_freeze_timer = 0.0

# ── Init pygame + assets ────────────────────────────────────
screen, scaled_vinyle, manager = init()
clock = pygame.time.Clock()

image_robot, rect_robot = create_robot_surface()

# ── Robot allié (vert) ──────────────────────────────────────
robot = Robot(scaled_vinyle, screen, image_robot)

# ── Robot ennemi (rouge) avec patrouille ────────────────────
image_ennemi = pygame.Surface(image_robot.get_size())
image_ennemi.fill((220, 30, 30))
image_ennemi.set_colorkey((0, 0, 0))
# Bande jaune pour distinguer l'avant de l'ennemi
px_w = image_ennemi.get_width()
pygame.draw.rect(image_ennemi, (255, 220, 0), (0, 0, px_w, 8))

robot_ennemi = RobotEnnemi(
    scaled_vinyle, screen, image_ennemi,
    waypoints=[
        (2500, 300),
        (2500, 1700),
        (1500, 1000),
        (500,  300),
        (500,  1700),
    ],
    patrol_speed=70,
)

# ── Sidebar ─────────────────────────────────────────────────
(ui_panel, lbl_init, ent_x, ent_y, ent_o, lbl_x, lbl_y, lbl_o,
 lbl_speed, ent_max_speed, ent_accel, ent_max_turning_speed, ent_turning_accel,
 lbl_max_speed, lbl_accel, lbl_max_turning_speed, lbl_turning_accel,
 lbl_file, ent_file, btn_apply, btn_start, btn_enregistrer,
 lbl_rec_file, ent_rec_file, btn_valid, lbl_mouse_coords, lbl_mouse_mm_valid,
 btn_stop, btn_pause, btn_face, btn_vitesse, btn_fonction,
 btn_match, lbl_timer
 ) = create_sidebar(manager, robot, enregistrement)


# ════════════════════════════════════════════════════════════
#  Boucle principale
# ════════════════════════════════════════════════════════════
while running:
    dt = clock.tick(FPS) / 1000.0   # secondes

    # ── Événements ──────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        manager.process_events(event)

        # Coordonnées souris en mm
        target_px_x, target_px_y = pygame.mouse.get_pos()
        mouse_mm_x = int(robot.conversion_From_px_x_To_mm_x(target_px_x))
        mouse_mm_y = int(robot.conversion_From_px_y_To_mmy(target_px_y))
        lbl_mouse_coords.set_text(f"Souris terrain: X={mouse_mm_x} mm, Y={mouse_mm_y} mm")

        if event.type == pygame_gui.UI_BUTTON_PRESSED:

            # Réinitialiser
            if event.ui_element == btn_apply:
                # Paramètres robot allié
                robot.mm_x        = parse_number(ent_x.get_text(), robot.mm_x)
                robot.mm_y        = parse_number(ent_y.get_text(), robot.mm_y)
                robot.angle       = parse_number(ent_o.get_text(), robot.angle)
                robot.max_speed   = parse_number(ent_max_speed.get_text(), robot.max_speed)
                robot.acceleration = parse_number(ent_accel.get_text(), robot.acceleration)
                robot.max_turning_speed  = parse_number(ent_max_turning_speed.get_text(), robot.max_turning_speed)
                robot.turning_acceleration = parse_number(ent_turning_accel.get_text(), robot.turning_acceleration)
                file_strat_path   = ent_file.get_text()
                # Stopper tous les mouvements du robot allié
                robot.state = IDLE
                robot._command_queue = []
                robot.speed = 0
                start_strat = False
                commands    = None
                # Réinitialiser le robot ennemi à sa position de départ et relancer sa patrouille
                robot_ennemi.mm_x  = 2500
                robot_ennemi.mm_y  = 1000
                robot_ennemi.angle = 180
                robot_ennemi.speed = 0
                robot_ennemi._command_queue = []
                robot_ennemi._wp_index = 0
                robot_ennemi._go_to_next_wp()
                print("Réinitialisé")

            # Démarrer stratégie
            elif event.ui_element == btn_start:
                try:
                    commands = parse_fdd_commands(file_strat_path)
                    print("Stratégie chargée:", commands)
                except Exception as e:
                    print(f"Erreur fichier stratégie : {e}")
                start_strat = True
                strategy_start_time = pygame.time.get_ticks() / 1000.0
                print("Démarrage stratégie…")

            # Enregistrement
            elif event.ui_element == btn_enregistrer:
                enregistrement = not enregistrement
                if enregistrement:
                    file_rec_path = ent_rec_file.get_text()
                    btn_enregistrer.set_text('Enregistrement ON')
                    file_rec_path = create_txt_file(file_rec_path)
                    write_rejoindre_command(robot.mm_x, robot.mm_y, file_rec_path, str(face_robot), str(vitesse_robot))
                else:
                    last_rec_path = file_rec_path  # sauvegarde le fichier créé
                    btn_enregistrer.set_text('Enregistrement OFF')
                    ent_rec_file.set_text('rec.txt')
                    print(f"Enregistrement arrêté : {last_rec_path}")

            # Validation : remet le robot à sa position initiale et rejoue le fichier
            elif event.ui_element == btn_valid:
                try:
                    path_to_play = last_rec_path if last_rec_path else file_rec_path
                    commands = parse_fdd_commands(path_to_play)
                    robot.mm_x  = parse_number(ent_x.get_text(), robot.mm_x)
                    robot.mm_y  = parse_number(ent_y.get_text(), robot.mm_y)
                    robot.angle = parse_number(ent_o.get_text(), robot.angle)
                    robot.state = IDLE
                    robot._command_queue = []
                    start_strat = True
                    strategy_start_time = pygame.time.get_ticks() / 1000.0
                    print(f"Exécution : {path_to_play}")
                except Exception as e:
                    print(f"Erreur : {e}")

            # Stop
            elif event.ui_element == btn_stop:
                start_strat = False
                stop_strat  = True
                pause_strat = False
                commands    = None
                robot.state = IDLE
                strategy_start_time = 0
                print("Stratégie stoppée")

            # Pause / Resume
            elif event.ui_element == btn_pause:
                if pause_strat:
                    pause_strat = False
                    btn_pause.set_text("Pause")
                else:
                    pause_strat = True
                    btn_pause.set_text("Resume")

            # Face avant/arrière
            elif event.ui_element == btn_face:
                face_robot = 1 - face_robot
                btn_face.set_text(f"Face: {face_robot}")

            # Vitesse cycle
            elif event.ui_element == btn_vitesse:
                opts = [25, 50, 75, 100]
                idx = opts.index(vitesse_robot) if vitesse_robot in opts else 3
                vitesse_robot = opts[(idx + 1) % len(opts)]
                btn_vitesse.set_text(f"Vitesse: {vitesse_robot}%")

            # Fonction rejoindre / orienter
            elif event.ui_element == btn_fonction:
                if fonction_robot == "rejoindre":
                    fonction_robot = "orienter"
                    btn_fonction.set_text("Fonction: Orienter")
                else:
                    fonction_robot = "rejoindre"
                    btn_fonction.set_text("Fonction: Rejoindre")

            # Lancer le match
            elif event.ui_element == btn_match:
                # Réinitialiser les robots à leur position initiale
                robot.mm_x  = parse_number(ent_x.get_text(), robot.mm_x)
                robot.mm_y  = parse_number(ent_y.get_text(), robot.mm_y)
                robot.angle = parse_number(ent_o.get_text(), robot.angle)
                robot.state = IDLE
                robot._command_queue = []
                robot.speed = 0
                # Réinitialiser l'ennemi
                robot_ennemi.mm_x  = 2500
                robot_ennemi.mm_y  = 1000
                robot_ennemi.angle = 180
                robot_ennemi._wp_index = 0
                robot_ennemi._go_to_next_wp()
                # Lancer le timer
                match_running    = True
                match_start_time = pygame.time.get_ticks() / 1000.0
                match_end_freeze = False
                match_freeze_timer = 0.0
                pause_strat = False
                btn_pause.set_text("Pause")
                lbl_timer.set_text("Match : 100s")
                print("Match lancé !")

        # Enregistrement : clic souris sur la carte
        if enregistrement:
            lbl_mouse_mm_valid.set_text(f"value: X={mouse_mm_x_valid} mm, Y={mouse_mm_y_valid} mm")
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if mouse_mm_x > 0 and mx < (Screen_WIDTH - UI_W):
                    mouse_mm_x_valid = mouse_mm_x
                    mouse_mm_y_valid = mouse_mm_y
                    if fonction_robot == "rejoindre":
                        write_rejoindre_command(mouse_mm_x_valid, mouse_mm_y_valid,
                                                file_rec_path, str(face_robot), str(vitesse_robot))
                    elif fonction_robot == "orienter":
                        write_orienter_command(robot.angle, file_rec_path, str(vitesse_robot))
                    robot.rejoindre(mouse_mm_x_valid, mouse_mm_y_valid, face_robot, vitesse_robot)
        else:
            lbl_mouse_mm_valid.set_text("")

        # Clic libre → rejoindre direct
        if (not enregistrement and not start_strat
                and event.type == pygame.MOUSEBUTTONDOWN
                and mouse_mm_x > 0
                and pygame.mouse.get_pos()[0] < (Screen_WIDTH - UI_W)):
            robot.rejoindre(mouse_mm_x, mouse_mm_y, 0, 100)

    # ── Fond ────────────────────────────────────────────────
    pygame.draw.rect(screen, (60, 60, 60),
                     pygame.Rect(0, 0, Screen_WIDTH - UI_W, Screen_HEIGHT))

    # ── Timer de match ───────────────────────────────────────
    if match_running:
        elapsed      = (pygame.time.get_ticks() / 1000.0) - match_start_time
        time_left    = max(0.0, MATCH_DURATION - elapsed)
        lbl_timer.set_text(f"Match : {int(time_left)}s")

        if time_left <= 0 and not match_end_freeze:
            # Fin du match : geler les robots 3 secondes
            match_end_freeze   = True
            match_freeze_timer = 0.0
            robot.state        = IDLE
            robot._command_queue = []
            robot.speed        = 0
            start_strat        = False
            print("Match terminé ! Gel 3 secondes…")

        if match_end_freeze:
            match_freeze_timer += dt
            lbl_timer.set_text(f"Fin du match ! ({int(3 - match_freeze_timer) + 1}s)")
            if match_freeze_timer >= 3.0:
                match_end_freeze = False
                match_running    = False
                lbl_timer.set_text("Match : --")
                # Remettre les robots à leur position initiale
                robot.mm_x  = parse_number(ent_x.get_text(), robot.mm_x)
                robot.mm_y  = parse_number(ent_y.get_text(), robot.mm_y)
                robot.angle = parse_number(ent_o.get_text(), robot.angle)
                robot.state = IDLE
                robot._command_queue = []
                robot.speed = 0
                robot_ennemi.mm_x  = 2500
                robot_ennemi.mm_y  = 1000
                robot_ennemi.angle = 180
                robot_ennemi._wp_index = 0
                robot_ennemi._go_to_next_wp()
                print("Robots remis à la position initiale.")

    # ── Chrono stratégie ────────────────────────────────────
    current_time = pygame.time.get_ticks() / 1000.0
    if robot.graphique:
        robot.graphique.update_strategy_time(
            current_time if strategy_start_time > 0 else 0,
            start_strat and not pause_strat)

    # ── Stratégie : passe la prochaine commande si le robot est IDLE ────
    if start_strat and not pause_strat:
        if robot.is_idle():
            strategie(robot, start_strat, commands)
            if not commands:
                start_strat = False
                print("Stratégie terminée !")

    # ── Mise à jour physique ─────────────────────────────────
    # L'ennemi peut gêner l'allié, mais pas l'inverse (simplification)
    if not pause_strat and not match_end_freeze:
        robot.adapter_vitesse(robot_ennemi, angle_vision=120, distance_securite=1000)
        robot.update(dt, obstacles=[robot_ennemi])

    if not match_end_freeze:
        robot_ennemi.update(dt, obstacles=None)   # l'ennemi ne s'arrête pas

    # ── Calcul distance pour affichage alerte ───────────────
    dist = math.hypot(robot.mm_x - robot_ennemi.mm_x,
                      robot.mm_y - robot_ennemi.mm_y)

    # ── Rendu unique (UN seul blit du fond par frame) ────────
    # 1. Fond
    if robot.graphique:
        robot.graphique.draw_background()

    # 2. Robots (ennemi derrière, allié devant)
    if robot_ennemi.graphique:
        robot_ennemi.graphique.draw_robot()
    if robot.graphique:
        robot.graphique.draw_robot()

    # 3. Cercle d'alerte collision
    if dist < COLLISION_DISTANCE:
        alert_px_x = int(robot.conversion_From_mmx_To_px_x(robot.mm_x))
        alert_px_y = int(robot.conversion_From_mmy_To_px_y(robot.mm_y))
        radius_px  = int((COLLISION_DISTANCE / 3000) * FIELD_WIDTH)
        pygame.draw.circle(screen, (255, 80, 80), (alert_px_x, alert_px_y), radius_px, 2)
        font_alert = pygame.font.Font(None, 22)
        txt = font_alert.render(f"⚠ Adversaire à {int(dist)} mm", True, (255, 80, 80))
        screen.blit(txt, (10, FIELD_HEIGHT - 30))

    # 4. UI sidebar
    manager.update(dt)
    manager.draw_ui(screen)

    # 5. HUD par-dessus la sidebar (après draw_ui pour ne pas être écrasé)
    if robot.graphique:
        robot.graphique.draw_hud()

    pygame.display.update()

pygame.quit()