import os
import xml.etree.ElementTree as ET

# Chemin vers le dossier contenant les fichiers XML de LabelImg
xml_folder = './datasets/dataset/labels'  # Remplacez par le chemin de votre dossier contenant les fichiers XML
image_folder = './datasets/dataset/images'     # Remplacez par le chemin de votre dossier contenant les images
output_folder = './datasets/dataset/labels'  # Dossier où seront stockées les annotations YOLO

# Liste des classes : ici on suppose que '0' correspond à la classe 0 et '1' à la classe 1
classes = ['t', 'ct']

# Créez le dossier de sortie s'il n'existe pas
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Fonction pour convertir les coordonnées
def convert_to_yolo_format(width, height, bbox):
    x_min, y_min, x_max, y_max = bbox
    # Normalisation des coordonnées
    x_center = (x_min + x_max) / 2.0 / width
    y_center = (y_min + y_max) / 2.0 / height
    w = (x_max - x_min) / width
    h = (y_max - y_min) / height
    return x_center, y_center, w, h

# Fonction pour lire les fichiers XML et créer les fichiers YOLO
def convert_xml_to_yolo(xml_file, image_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Obtenir la largeur et la hauteur de l'image
    size = root.find('size')
    width = int(size.find('width').text)
    height = int(size.find('height').text)

    # Créer un fichier de sortie pour YOLO
    yolo_file = os.path.join(output_folder, os.path.basename(image_file).replace('.jpg', '.txt'))

    with open(yolo_file, 'w') as f:
        for obj in root.iter('object'):
            class_name = obj.find('name').text.strip()
            # Vérifier si le nom correspond à l'une des deux classes
            if class_name == '0':
                class_id = 0
            elif class_name == '1':
                class_id = 1
            else:
                # Si l'objet n'appartient pas aux classes "0" ou "1", on le saute
                continue
            
            bbox = obj.find('bndbox')
            x_min = int(bbox.find('xmin').text)
            y_min = int(bbox.find('ymin').text)
            x_max = int(bbox.find('xmax').text)
            y_max = int(bbox.find('ymax').text)
            
            # Convertir en format YOLO
            x_center, y_center, w, h = convert_to_yolo_format(width, height, (x_min, y_min, x_max, y_max))
            
            # Écrire les données au format YOLO
            f.write(f"{class_id} {x_center} {y_center} {w} {h}\n")

# Lister tous les fichiers XML dans le dossier d'annotations
for xml_file in os.listdir(xml_folder):
    if xml_file.endswith('.xml'):
        # Trouver le fichier image correspondant
        image_file = os.path.join(image_folder, xml_file.replace('.xml', '.jpg'))
        
        # Convertir le XML en format YOLO
        convert_xml_to_yolo(os.path.join(xml_folder, xml_file), image_file)

print("Conversion terminée !")