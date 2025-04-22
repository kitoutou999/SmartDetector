import pyautogui
import keyboard
from datetime import datetime
import time
import os
import uuid
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
CAPTURE_SIZE = 640

left = (SCREEN_WIDTH // 2) - (CAPTURE_SIZE // 2)
top = (SCREEN_HEIGHT // 2) - (CAPTURE_SIZE // 2)
region = (left, top, CAPTURE_SIZE, CAPTURE_SIZE)

def compter_screens():
    chemin = "datasets/dataset/negatives"
    if not os.path.exists(chemin):
        return 0
    return len([f for f in os.listdir(chemin) if f.endswith('.png')])

def capture_ecran():
    img = pyautogui.screenshot(region=region)
    filename = datetime.now().strftime("capture_"+str(uuid.uuid4())[:10]+".png")
    img.save("datasets/dataset/negatives/"+filename)
    count = compter_screens()
    print(f"Capture sauvegardée : {filename} | Total: {count}")

t_pressed = False

print("Appuyez sur T pour capturer l'écran | W pour quitter")

while True:
    if keyboard.is_pressed('w'):
        break
    
    if keyboard.is_pressed('t'):
        if not t_pressed:
            capture_ecran()
            t_pressed = True
    else:
        t_pressed = False
    
    time.sleep(0.01)