import mmap
import random
import numpy as np
import pyautogui
import keyboard
import time
import ctypes


SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
BYTES_PER_PIXEL = 3
MEMORY_SIZE = SCREEN_WIDTH * SCREEN_HEIGHT * BYTES_PER_PIXEL

aspect_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
window_width = 1280
window_height = int(window_width / aspect_ratio)





pyautogui.FAILSAFE = False

# --- Définition de SendInput pour simuler le mouvement souris en position absolue ---
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000

PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("mi", MouseInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def move_mouse_absolute(x, y):
    """
    Déplace le curseur à la position (x, y) en coordonnées absolues,
    normalisées sur l'échelle [0, 65535] pour SendInput.
    """
    for i in range(10):
        # Générer un déplacement aléatoire en pixels sur X et Y
        dx = random.randint(-100, 100)
        dy = random.randint(-100, 100)
        duration = 0.2  # durée du mouvement
        pyautogui.moveRel(dx, dy, duration=duration)
        print(f"Mouvement {i+1}: déplacement de ({dx}, {dy})")
        time.sleep(0.5)
    print("Moving to", x, y)


def aim_at_closest_target():
    """Vise la cible (détection de personne) la plus proche du centre de l'écran
       et déplace le curseur via SendInput.
    """    
    randomposx = np.random.randint(0, SCREEN_WIDTH)
    randomposy = np.random.randint(0, SCREEN_HEIGHT)
    print("Aiming at", randomposx, randomposy)
    move_mouse_absolute(randomposx, randomposy)
running = True

def on_quit():
    global running
    running = False

# Configuration des touches : 'q' pour quitter
keyboard.on_press_key('q', lambda _: on_quit())

print("Memory size =", MEMORY_SIZE)
while running:
    if keyboard.is_pressed('t'):
        aim_at_closest_target()


