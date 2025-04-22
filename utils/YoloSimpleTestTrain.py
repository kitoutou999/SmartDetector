import tkinter as tk
from tkinter import filedialog
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image, ImageTk


model = YOLO('runs/detect/train7/weights/best.pt') 

def load_image():
    file_path = filedialog.askopenfilename(title="Choisir une image", filetypes=[("Images", "*.jpg;*.jpeg;*.png")])
    
    if file_path:
        image = cv2.imread(file_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        results = model(image_rgb)
        
        annotated_image = results[0].plot() 
        
        # Convertir l'image annotée pour l'affichage Tkinter
        annotated_image_pil = Image.fromarray(annotated_image)
        annotated_image_tk = ImageTk.PhotoImage(annotated_image_pil)

        label_img.config(image=annotated_image_tk)
        label_img.image = annotated_image_tk

root = tk.Tk()
root.title("Détection d'Ennemis avec YOLOv8")
root.geometry("800x600")

button_load = tk.Button(root, text="Charger une image", command=load_image)
button_load.pack(pady=20)

label_img = tk.Label(root)
label_img.pack(padx=10, pady=10)

root.mainloop()
