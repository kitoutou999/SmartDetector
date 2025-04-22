import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import xml.etree.ElementTree as ET
import os
from pathlib import Path

class ImageAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("XML Image Annotator")
        # Agrandir la taille de la fenêtre
        self.root.geometry("1280x960")  

        # Variables
        self.current_xml_index = 0  # Démarrer à l'index 517
        self.current_box_index = 0
        self.xml_files = []
        self.current_boxes = []
        self.modified_names = {}
        # Dimensions d'affichage de l'image
        self.display_width = 1000  
        self.display_height = 600  
        
        # Interface setup
        self.setup_ui()

        # Raccourcis clavier pour les macros :
        # Touche 'k' pour annoter avec "0"
        self.root.bind('k', lambda event: self.annotate_box("0"))
        # Touche 'l' pour annoter avec "1"
        self.root.bind('l', lambda event: self.annotate_box("1"))
        
        # Charger les fichiers XML
        self.load_xml_files()
        
        if self.xml_files:
            self.load_current_xml()

    def setup_ui(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Canvas pour l'image avec nouvelle taille
        self.canvas = tk.Canvas(self.main_frame, width=self.display_width, height=self.display_height)
        self.canvas.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Boutons pour la navigation
        self.btn_frame = ttk.Frame(self.main_frame)
        self.btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.btn_0 = ttk.Button(self.btn_frame, text="0", command=lambda: self.annotate_box("0"))
        self.btn_0.grid(row=0, column=0, padx=5)
        
        self.btn_1 = ttk.Button(self.btn_frame, text="1", command=lambda: self.annotate_box("1"))
        self.btn_1.grid(row=0, column=1, padx=5)
        
        # Labels d'information
        self.info_label = ttk.Label(self.main_frame, text="")
        self.info_label.grid(row=2, column=0, columnspan=2)
        
        self.progress_label = ttk.Label(self.main_frame, text="")
        self.progress_label.grid(row=3, column=0, columnspan=2)

    def load_xml_files(self):
        # Chemin vers le dossier des labels
        xml_path = Path(os.getcwd()) / "dataset" / "labels"
        self.xml_files = sorted(list(xml_path.glob("*.xml")))
        self.update_progress_label()

    def get_first_xml_path(self):
        xml_path = Path(os.getcwd()) / "dataset" / "labels"
        first_xml = list(xml_path.glob("*.xml"))
        if first_xml:
            return str(first_xml[0])
        else:
            return ""

    def load_current_xml(self):
        if 0 <= self.current_xml_index < len(self.xml_files):
            xml_file = self.xml_files[self.current_xml_index]
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Obtenir les dimensions originales de l'image
            original_width = int(root.find('.//width').text)
            original_height = int(root.find('.//height').text)
            
            # Calculer les ratios de redimensionnement
            self.scale_x = self.display_width / original_width
            self.scale_y = self.display_height / original_height
            
            # Charger l'image
            image_path = Path(root.find('path').text)
            if not image_path.exists():
                image_path = Path(xml_file).parent / root.find('filename').text
            
            try:
                image = Image.open(image_path)
                # Redimensionner l'image pour la nouvelle taille d'affichage
                image = image.resize((self.display_width, self.display_height), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(image)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
                
                # Charger les boxes
                self.current_boxes = []
                for obj in root.findall('.//object'):
                    bbox = obj.find('bndbox')
                    name = obj.find('name').text
                    
                    # Appliquer le ratio de redimensionnement
                    x1 = int(float(bbox.find('xmin').text) * self.scale_x)
                    y1 = int(float(bbox.find('ymin').text) * self.scale_y)
                    x2 = int(float(bbox.find('xmax').text) * self.scale_x)
                    y2 = int(float(bbox.find('ymax').text) * self.scale_y)
                    
                    self.current_boxes.append({
                        'coords': (x1, y1, x2, y2),
                        'name': name
                    })
                
                self.current_box_index = 0
                self.draw_current_box()
                self.update_progress_label()
                
            except Exception as e:
                self.info_label.config(text=f"Erreur lors du chargement de l'image: {str(e)}")

    def draw_current_box(self):
        self.canvas.delete("box")
        for i, box in enumerate(self.current_boxes):
            x1, y1, x2, y2 = box['coords']
            # La box en cours est en bleu, les autres en rouge
            color = "blue" if i == self.current_box_index else "red"
            name = self.modified_names.get(f"{self.current_xml_index}_{i}", box['name'])
            
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2, tags="box")
            self.canvas.create_text(x1, y1-10, text=name, fill=color, tags="box")
        
        self.info_label.config(text=f"Box {self.current_box_index + 1}/{len(self.current_boxes)}")

    def annotate_box(self, value):
        if self.current_boxes:
            key = f"{self.current_xml_index}_{self.current_box_index}"
            self.modified_names[key] = value
            
            self.current_box_index += 1
            
            if self.current_box_index >= len(self.current_boxes):
                self.save_current_xml()
                self.current_xml_index += 1
                self.current_box_index = 0
                
                if self.current_xml_index >= len(self.xml_files):
                    self.info_label.config(text="Annotation terminée!")
                    return
                
                self.load_current_xml()
            else:
                self.draw_current_box()

    def save_current_xml(self):
        if 0 <= self.current_xml_index < len(self.xml_files):
            xml_file = self.xml_files[self.current_xml_index]
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            objects = root.findall('.//object')
            for i, obj in enumerate(objects):
                key = f"{self.current_xml_index}_{i}"
                if key in self.modified_names:
                    obj.find('name').text = self.modified_names[key]
            
            tree.write(xml_file)

    def update_progress_label(self):
        if self.xml_files and 0 <= self.current_xml_index < len(self.xml_files):
            file_name = os.path.basename(str(self.xml_files[self.current_xml_index]))
            message = f"XML {self.current_xml_index + 1}/{len(self.xml_files)} : {file_name}"
        else:
            message = "Aucun fichier XML."
        self.progress_label.config(text=message)

def main():
    root = tk.Tk()
    app = ImageAnnotator(root)
    root.mainloop()

if __name__ == "__main__":
    main()