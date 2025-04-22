import mmap
import numpy as np
import cv2
import win32event
import win32file
import os
from pathlib import Path
from typing import List, Optional
from ultralytics import YOLO
import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("ultralytics").setLevel(logging.WARNING)


# Configuration globale
class Config:
    # Paramètres mémoire partagée
    MEMORY_NAME = "Global\\ScreenshotSharedMemory"
    MUTEX_NAME = "Global\\ScreenshotMutex"
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    BYTES_PER_PIXEL = 3
    MEMORY_SIZE = SCREEN_WIDTH * SCREEN_HEIGHT * BYTES_PER_PIXEL

    # Chemins des datasets
    DATASET_ROOT = Path("datasets/dataset")
    IMAGES_DIR = DATASET_ROOT / "images"
    LABELS_DIR = DATASET_ROOT / "labelimg"
    COUNTER_FILE = IMAGES_DIR / "counter.txt"

    # Affichage
    WINDOW_NAME = "ScreenLive"
    WINDOW_WIDTH = 1280


# Initialisation des répertoires
Config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
Config.LABELS_DIR.mkdir(parents=True, exist_ok=True)


def initialize_memory() -> tuple:
    """Initialise la mémoire partagée et le mutex"""
    mutex = win32event.CreateMutex(None, False, Config.MUTEX_NAME)
    memory = mmap.mmap(-1, Config.MEMORY_SIZE, Config.MEMORY_NAME, access=mmap.ACCESS_READ)
    return mutex, memory


def create_xml_annotation(image_index: int, boxes: List, filename: str) -> None:
    """Crée un fichier d'annotation XML au format PASCAL VOC"""

    def add_element(parent, tag: str, text: str = "") -> ET.Element:
        element = ET.SubElement(parent, tag)
        element.text = str(text)
        return element

    # Création de la structure XML
    annotation = ET.Element("annotation")

    add_element(annotation, "folder", "images")
    add_element(annotation, "filename", filename)
    add_element(annotation, "path", Config.IMAGES_DIR / filename)

    source = add_element(annotation, "source")
    add_element(source, "database", "Unknown")

    size = add_element(annotation, "size")
    add_element(size, "width", Config.SCREEN_WIDTH)
    add_element(size, "height", Config.SCREEN_HEIGHT)
    add_element(size, "depth", Config.BYTES_PER_PIXEL)
    add_element(annotation, "segmented", 0)

    # Ajout des objets détectés
    for box in boxes:
        obj = add_element(annotation, "object")
        add_element(obj, "name", int(box.cls))
        add_element(obj, "pose", "Unspecified")
        add_element(obj, "truncated", 0)
        add_element(obj, "difficult", 0)

        bndbox = add_element(obj, "bndbox")
        coords = [int(x) for x in box.xyxy[0].tolist()]
        add_element(bndbox, "xmin", coords[0])
        add_element(bndbox, "ymin", coords[1])
        add_element(bndbox, "xmax", coords[2])
        add_element(bndbox, "ymax", coords[3])

    # Formatage et sauvegarde
    xml_str = minidom.parseString(ET.tostring(annotation)).toprettyxml(indent="\t", encoding="utf-8")
    xml_path = Config.LABELS_DIR / f"capture_{image_index}.xml"

    with open(xml_path, "wb") as f:
        f.write(xml_str)
    logger.info(f"Annotation sauvegardée : {xml_path}")


def load_image_counter() -> int:
    """Charge ou initialise le compteur d'images"""
    try:
        if Config.COUNTER_FILE.exists():
            return int(Config.COUNTER_FILE.read_text().strip())
    except Exception as e:
        logger.warning(f"Erreur lecture compteur : {e}")
    return 0


def main():
    """Workflow principal de capture et détection"""
    # Initialisation
    mutex, memory = initialize_memory()
    model = YOLO('csgo_detector.pt')
    image_counter = load_image_counter()
    capture_done = False

    # Configuration fenêtre
    cv2.namedWindow(Config.WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(Config.WINDOW_NAME, Config.WINDOW_WIDTH,
                     int(Config.WINDOW_WIDTH / (Config.SCREEN_WIDTH / Config.SCREEN_HEIGHT)))

    try:
        while True:
            # Acquisition du mutex
            if win32event.WaitForSingleObject(mutex, 100) != win32event.WAIT_OBJECT_0:
                continue

            try:
                raw_data = memory.read(Config.MEMORY_SIZE)
                memory.seek(0)

                if len(raw_data) != Config.MEMORY_SIZE:
                    continue

                # Conversion image
                frame = np.frombuffer(raw_data, dtype=np.uint8).reshape(
                    (Config.SCREEN_HEIGHT, Config.SCREEN_WIDTH, 3))

                # Détection YOLO
                results = model(frame)
                detections = results[0].boxes
                has_player = any(model.names[int(cls)] == 'player' for cls in detections.cls)

                # Logique de capture
                if has_player and not capture_done:
                    filename = f"capture_{image_counter}.jpg"
                    image_path = Config.IMAGES_DIR / filename

                    if cv2.imwrite(str(image_path), frame):
                        create_xml_annotation(image_counter, detections, filename)
                        image_counter += 1
                        Config.COUNTER_FILE.write_text(str(image_counter))
                        capture_done = True
                        logger.info(f"Capture {image_counter} sauvegardée")
                elif not has_player:
                    capture_done = False

                # Affichage
                cv2.imshow(Config.WINDOW_NAME, results[0].plot())

            finally:
                win32event.ReleaseMutex(mutex)

            # Gestion sortie
            if cv2.waitKey(40) & 0xFF == ord('q'):
                break

    finally:
        cv2.destroyAllWindows()
        memory.close()
        win32file.CloseHandle(mutex)
        logger.info("Nettoyage terminé")


if __name__ == "__main__":
    main()