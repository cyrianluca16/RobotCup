import pygame
import pygame_gui
from pygame_gui.elements import (UIPanel, UILabel, UITextEntryLine,
                                  UIButton, UIScrollingContainer)
from setup import Screen_WIDTH, Screen_HEIGHT, FIELD_WIDTH, FIELD_HEIGHT

W, H = Screen_WIDTH, Screen_HEIGHT
UI_W = Screen_WIDTH - FIELD_WIDTH
HUD_H = 28       # hauteur du label HUD fixe en haut
CONTENT_H = 820  # hauteur totale du contenu scrollable

def parse_number(s, default, integer=True):
    try:
        v = float(s.replace(',', '.'))
        return int(v) if integer else v
    except Exception:
        return default

def create_sidebar(manager, robot, enregistrement):
    # Panel fixe
    ui_panel = UIPanel(relative_rect=pygame.Rect(W-UI_W, 0, UI_W, H), manager=manager)

    # ── HUD fixe en haut (ne scrolle pas) ────────────────────
    lbl_hud = UILabel(
        pygame.Rect(0, 0, UI_W, HUD_H),
        text="X: -- mm, Y: -- mm, O: --",
        manager=manager, container=ui_panel)

    # ── Container scrollable sous le HUD ─────────────────────
    scroll = UIScrollingContainer(
        relative_rect=pygame.Rect(0, HUD_H, UI_W, H - HUD_H),
        manager=manager,
        container=ui_panel
    )
    scroll.set_scrollable_area_dimensions((UI_W - 20, CONTENT_H))
    C = scroll

    # ── Init x, y, o ─────────────────────────────────────────
    lw = int(UI_W * 0.25)
    ew = int((UI_W - lw - 50) / 3)
    y = 10

    lbl_init = UILabel(pygame.Rect(10, y, lw, 28), text="init:", manager=manager, container=C)
    lbl_x    = UILabel(pygame.Rect(10+lw, y+30, ew, 18), text="x", manager=manager, container=C)
    ent_x    = UITextEntryLine(pygame.Rect(10+lw, y, ew, 28), manager=manager, container=C)
    ent_x.set_text(str(robot.mm_x))
    lbl_y    = UILabel(pygame.Rect(10+lw+ew+5, y+30, ew, 18), text="y", manager=manager, container=C)
    ent_y    = UITextEntryLine(pygame.Rect(10+lw+ew+5, y, ew, 28), manager=manager, container=C)
    ent_y.set_text(str(robot.mm_y))
    lbl_o    = UILabel(pygame.Rect(10+lw+2*(ew+5), y+30, ew, 18), text="o", manager=manager, container=C)
    ent_o    = UITextEntryLine(pygame.Rect(10+lw+2*(ew+5), y, ew, 28), manager=manager, container=C)
    ent_o.set_text(str(robot.angle))

    # ── Vitesses ──────────────────────────────────────────────
    sw = int(UI_W * 0.25)
    vw = int((UI_W - sw - 50) / 4)
    y = 62

    lbl_speed             = UILabel(pygame.Rect(0, y, sw, 28), text="vitesse:", manager=manager, container=C)
    lbl_max_speed         = UILabel(pygame.Rect(sw, y+30, vw, 18), text="Vmax", manager=manager, container=C)
    ent_max_speed         = UITextEntryLine(pygame.Rect(sw, y, vw, 28), manager=manager, container=C)
    ent_max_speed.set_text(str(robot.max_speed))
    lbl_accel             = UILabel(pygame.Rect(sw+vw+5, y+30, vw, 18), text="Acc", manager=manager, container=C)
    ent_accel             = UITextEntryLine(pygame.Rect(sw+vw+5, y, vw, 28), manager=manager, container=C)
    ent_accel.set_text(str(robot.acceleration))
    lbl_max_turning_speed = UILabel(pygame.Rect(sw+2*(vw+5), y+30, vw, 18), text="VRot", manager=manager, container=C)
    ent_max_turning_speed = UITextEntryLine(pygame.Rect(sw+2*(vw+5), y, vw, 28), manager=manager, container=C)
    ent_max_turning_speed.set_text(str(robot.max_turning_speed))
    lbl_turning_accel     = UILabel(pygame.Rect(sw+3*(vw+5), y+30, vw, 18), text="ARot", manager=manager, container=C)
    ent_turning_accel     = UITextEntryLine(pygame.Rect(sw+3*(vw+5), y, vw, 28), manager=manager, container=C)
    ent_turning_accel.set_text(str(robot.turning_acceleration))

    # ── Strat file ────────────────────────────────────────────
    y = 118
    lbl_file = UILabel(pygame.Rect(10, y, 80, 28), text="strat file:", manager=manager, container=C)
    ent_file = UITextEntryLine(pygame.Rect(95, y, UI_W-115, 28), manager=manager, container=C)
    ent_file.set_text("test_V2.txt")

    bw = (UI_W - 30) // 2

    y = 153
    btn_apply = UIButton(pygame.Rect(10, y, bw, 34), text="Réinitialiser", manager=manager, container=C)
    btn_start = UIButton(pygame.Rect(20+bw, y, bw, 34), text="Start", manager=manager, container=C)

    y = 193
    btn_stop  = UIButton(pygame.Rect(10, y, bw, 34), text="Stop",  manager=manager, container=C)
    btn_pause = UIButton(pygame.Rect(20+bw, y, bw, 34), text="Pause", manager=manager, container=C)

    y = 233
    lbl_rec_file = UILabel(pygame.Rect(10, y, 80, 28), text="rec file:", manager=manager, container=C)
    ent_rec_file = UITextEntryLine(pygame.Rect(95, y, UI_W-115, 28), manager=manager, container=C)
    ent_rec_file.set_text("rec.txt")

    y = 268
    btn_valid       = UIButton(pygame.Rect(10, y, bw, 34), text="Validation",   manager=manager, container=C)
    btn_enregistrer = UIButton(pygame.Rect(20+bw, y, bw, 34), text="Enregistrer", manager=manager, container=C)

    y = 308
    btn_face    = UIButton(pygame.Rect(10, y, bw, 34), text="Face: 0",        manager=manager, container=C)
    btn_vitesse = UIButton(pygame.Rect(20+bw, y, bw, 34), text="Vitesse: 100%", manager=manager, container=C)

    y = 348
    btn_fonction = UIButton(pygame.Rect(10, y, UI_W-30, 34), text="Fonction: Rejoindre", manager=manager, container=C)

    y = 390
    btn_match = UIButton(pygame.Rect(10, y, UI_W-30, 38), text="Lancer le Match (100s)", manager=manager, container=C)

    y = 433
    lbl_timer = UILabel(pygame.Rect(10, y, UI_W-30, 26), text="Match : --", manager=manager, container=C)

    y = 463
    lbl_mouse_mm_valid = UILabel(pygame.Rect(10, y, UI_W-30, 22), text="", manager=manager, container=C)
    y = 488
    lbl_mouse_coords   = UILabel(pygame.Rect(10, y, UI_W-30, 22), text="Souris: X=0 mm, Y=0 mm", manager=manager, container=C)

    y = 520
    UILabel(pygame.Rect(10, y, UI_W-30, 22), text="Robot ennemi :", manager=manager, container=C)

    y = 546
    be = (UI_W - 30) // 2
    btn_ennemi_aleatoire = UIButton(pygame.Rect(10, y, be, 34),    text="Aleatoire",    manager=manager, container=C)
    btn_ennemi_charger   = UIButton(pygame.Rect(20+be, y, be, 34), text="Charger TXT",  manager=manager, container=C)

    y = 586
    ent_ennemi_file = UITextEntryLine(pygame.Rect(10, y, UI_W-30, 28), manager=manager, container=C)
    ent_ennemi_file.set_text("ennemi.txt")

    return (ui_panel, lbl_init, ent_x, ent_y, ent_o, lbl_x, lbl_y, lbl_o,
            lbl_speed, ent_max_speed, ent_accel, ent_max_turning_speed, ent_turning_accel,
            lbl_max_speed, lbl_accel, lbl_max_turning_speed, lbl_turning_accel,
            lbl_file, ent_file, btn_apply, btn_start, btn_enregistrer,
            lbl_rec_file, ent_rec_file, btn_valid, lbl_mouse_coords, lbl_mouse_mm_valid,
            btn_stop, btn_pause, btn_face, btn_vitesse, btn_fonction,
            btn_match, lbl_timer,
            btn_ennemi_aleatoire, btn_ennemi_charger, ent_ennemi_file,
            lbl_hud)
