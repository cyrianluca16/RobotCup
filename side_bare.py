import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UITextEntryLine, UIButton, UIHorizontalSlider
from setup import Screen_WIDTH, Screen_HEIGHT, FIELD_WIDTH, FIELD_HEIGHT

W, H = Screen_WIDTH, Screen_HEIGHT
UI_W = Screen_WIDTH - FIELD_WIDTH

def parse_number(s, default, integer=True):
    try:
        v = float(s.replace(',', '.'))
        return int(v) if integer else v
    except Exception:
        return default

def create_sidebar(manager,robot, enregistrement):
    ui_panel = UIPanel(relative_rect=pygame.Rect(W-UI_W, 0, UI_W, H), manager=manager)

        # Ligne compacte pour init x, y, o
    label_width = int(UI_W * 0.25)
    entry_width = int((UI_W - label_width - 30) / 3)
    y_line = int(H * 0.05)

    lbl_init = UILabel(relative_rect=pygame.Rect(10, y_line, label_width, 30), text="init:", manager=manager, container=ui_panel)

    lbl_x = UILabel(relative_rect=pygame.Rect(10 + label_width, y_line + 28, entry_width, 20), text="x", manager=manager, container=ui_panel)
    ent_x = UITextEntryLine(relative_rect=pygame.Rect(10 + label_width, y_line, entry_width, 30), manager=manager, container=ui_panel)
    ent_x.set_text(str(robot.mm_x))

    lbl_y = UILabel(relative_rect=pygame.Rect(10 + label_width + entry_width + 5, y_line + 28, entry_width, 20), text="y", manager=manager, container=ui_panel)
    ent_y = UITextEntryLine(relative_rect=pygame.Rect(10 + label_width + entry_width + 5, y_line, entry_width, 30), manager=manager, container=ui_panel) 
    ent_y.set_text(str(robot.mm_y))
    
    lbl_o = UILabel(relative_rect=pygame.Rect(10 + label_width + 2 * (entry_width + 5), y_line + 28, entry_width, 20), text="o", manager=manager, container=ui_panel)
    ent_o = UITextEntryLine(relative_rect=pygame.Rect(10 + label_width + 2 * (entry_width + 5), y_line, entry_width, 30), manager=manager, container=ui_panel)
    ent_o.set_text(str(robot.angle))

        # Ligne compacte pour vitesses et accélérations
    speed_label_width = int(UI_W * 0.25)
    speed_entry_width = int((UI_W - speed_label_width - 40) / 4)
    y_speed_line = int(H * 0.13)

    lbl_speed = UILabel(relative_rect=pygame.Rect(0, y_speed_line, speed_label_width, 30), text="vitesse:", manager=manager, container=ui_panel)

    lbl_max_speed = UILabel(relative_rect=pygame.Rect(0 + speed_label_width, y_speed_line + 28, speed_entry_width, 20), text="Vmax", manager=manager, container=ui_panel)
    ent_max_speed = UITextEntryLine(relative_rect=pygame.Rect(0 + speed_label_width, y_speed_line, speed_entry_width, 30), manager=manager, container=ui_panel)
    ent_max_speed.set_text(str(robot.max_speed))

    lbl_accel = UILabel(relative_rect=pygame.Rect(0 + speed_label_width + speed_entry_width + 5, y_speed_line + 28, speed_entry_width, 20), text="Acc", manager=manager, container=ui_panel)
    ent_accel = UITextEntryLine(relative_rect=pygame.Rect(0 + speed_label_width + speed_entry_width + 5, y_speed_line, speed_entry_width, 30), manager=manager, container=ui_panel)
    ent_accel.set_text(str(robot.acceleration))

    lbl_max_turning_speed = UILabel(relative_rect=pygame.Rect(0 + speed_label_width + 2 * (speed_entry_width + 5), y_speed_line + 28, speed_entry_width, 20), text="VRot", manager=manager, container=ui_panel)
    ent_max_turning_speed = UITextEntryLine(relative_rect=pygame.Rect(0 + speed_label_width + 2 * (speed_entry_width + 5), y_speed_line, speed_entry_width, 30), manager=manager, container=ui_panel)
    ent_max_turning_speed.set_text(str(robot.max_turning_speed))

    lbl_turning_accel = UILabel(relative_rect=pygame.Rect(0 + speed_label_width + 3 * (speed_entry_width + 5), y_speed_line + 28, speed_entry_width, 20), text="ARot", manager=manager, container=ui_panel)
    ent_turning_accel = UITextEntryLine(relative_rect=pygame.Rect(0 + speed_label_width + 3 * (speed_entry_width + 5), y_speed_line, speed_entry_width, 30), manager=manager, container=ui_panel)
    ent_turning_accel.set_text(str(robot.turning_acceleration))

        # Input text
    lbl_file = UILabel(relative_rect=pygame.Rect(10, 130, 80, 30), text="strat file :", manager=manager, container=ui_panel)
    ent_file = UITextEntryLine(relative_rect=pygame.Rect(100, 130, UI_W-110, 30), manager=manager, container=ui_panel)
    ent_file.set_text("test_V2.txt")  # Valeur par défaut (sera cherché dans strategie_txt)

        # Boutons Appliquer et Start
    btn_width_1 = (UI_W - 30) // 2
    y_btn_line_1 = 170
    
    btn_apply = UIButton(relative_rect=pygame.Rect(10, y_btn_line_1, btn_width_1, 36), text="Appliquer", manager=manager, container=ui_panel)
    btn_start = UIButton(relative_rect=pygame.Rect(20 + btn_width_1, y_btn_line_1, btn_width_1, 36), text="Start", manager=manager, container=ui_panel)

        # Boutons Stop et Pause
    btn_width_control = (UI_W - 30) // 2
    y_btn_control = 210
    
    btn_stop = UIButton(relative_rect=pygame.Rect(10, y_btn_control, btn_width_control, 36), text="Stop", manager=manager, container=ui_panel)
    btn_pause = UIButton(relative_rect=pygame.Rect(20 + btn_width_control, y_btn_control, btn_width_control, 36), text="Pause", manager=manager, container=ui_panel)

    lbl_rec_file = UILabel(relative_rect=pygame.Rect(10, 250, 80, 30), text="rec file :", manager=manager, container=ui_panel)
    ent_rec_file = UITextEntryLine(relative_rect=pygame.Rect(100, 250, UI_W-110, 30), manager=manager, container=ui_panel)
    ent_rec_file.set_text("rec.txt")

        # Boutons de commandes
    btn_width_2 = (UI_W - 30) // 2
    y_btn_line_2 = 290

    btn_valid = UIButton(relative_rect=pygame.Rect(10, y_btn_line_2, btn_width_2, 36),  text="Validation", manager=manager,container=ui_panel)
    btn_enregistrer = UIButton(relative_rect=pygame.Rect(20 + btn_width_2, y_btn_line_2, btn_width_2, 36),text="Enregistrer",manager=manager,container=ui_panel)

        # Boutons Face et Vitesse
    btn_width_3 = (UI_W - 30) // 2
    y_btn_line_3 = 330

    btn_face = UIButton(relative_rect=pygame.Rect(10, y_btn_line_3, btn_width_3, 36), text="Face: 0", manager=manager, container=ui_panel)
    btn_vitesse = UIButton(relative_rect=pygame.Rect(20 + btn_width_3, y_btn_line_3, btn_width_3, 36), text="Vitesse: 100%", manager=manager, container=ui_panel)

        # Bouton Fonction (Toggle Rejoindre/Orienter)
    btn_width_4 = UI_W - 20
    y_btn_line_4 = 370

    btn_fonction = UIButton(relative_rect=pygame.Rect(10, y_btn_line_4, btn_width_4, 36), text="Fonction: Rejoindre", manager=manager, container=ui_panel)

        # label mouse
    lbl_mouse_coords = UILabel(relative_rect=pygame.Rect(10, 530, UI_W-20, 30),text="Souris terrain: X=0 mm, Y=0 mm",manager=manager,container=ui_panel)
    lbl_mouse_mm_valid = UILabel(relative_rect=pygame.Rect(10, 450, UI_W-20, 30),text="Value mm: X=0 mm, Y=0 mm",manager=manager,container=ui_panel)

    return (ui_panel, lbl_init, ent_x, ent_y, ent_o, lbl_x, lbl_y, lbl_o,
            lbl_speed, ent_max_speed, ent_accel, ent_max_turning_speed, ent_turning_accel,
            lbl_max_speed, lbl_accel, lbl_max_turning_speed, lbl_turning_accel,
            lbl_file, ent_file, btn_apply, btn_start, btn_enregistrer,
            lbl_rec_file, ent_rec_file, btn_valid, lbl_mouse_coords, lbl_mouse_mm_valid,
            btn_stop, btn_pause, btn_face, btn_vitesse, btn_fonction)
