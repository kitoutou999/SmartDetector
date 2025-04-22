# ScreenFast

ScreenFast est un projet de détection d'objets en temps réel utilisant YOLO (You Only Look Once) pour l'analyse d'écran. Le projet est particulièrement optimisé pour la détection d'objets dans des jeux vidéo comme CS:GO.

## Fonctionnalités

- Capture d'écran en temps réel
- Détection d'objets avec YOLO
- Entraînement personnalisé du modèle
- Support GPU et CPU
- Interface visuelle pour la visualisation des détections

## Prérequis

- Python
- PyTorch
- OpenCV (cv2)
- Ultralytics YOLO
- win32event et win32file (pour Windows)
- CUDA (optionnel, pour l'accélération GPU)

## Utilisation

### Entraînement du modèle

Pour entraîner le modèle avec la configuration CPU (local) :
```bash
python YoloTrain.py
```

Pour entraîner avec la configuration GPU (serveur) :
```bash
python YoloTrain.py --use_server True
```

### Détection en temps réel

Pour lancer la détection en temps réel :
```bash
python YoloRealTime.py
```

Appuyez sur 'q' pour quitter l'application.

## Structure du projet

- `YoloTrain.py` : Script d'entraînement du modèle YOLO
- `YoloRealTime.py` : Script de détection en temps réel
- `data.yaml` : Configuration des données d'entraînement
- `utils/` : Utilitaires et fonctions auxiliaires
- `runs/` : Dossier contenant les résultats d'entraînement
- `datasets/` : Dossier pour les données d'entraînement
- `yolo11n.pt` : Modèle de base YOLO
- `csgo_detector.pt` : Modèle entraîné personnalisé

## Configuration

Le projet utilise deux configurations principales :

1. **Configuration CPU (local)**
   - Optimisé pour l'utilisation sur CPU
   - Batch size plus petit
   - Nombre d'époques réduit

2. **Configuration GPU (serveur)**
   - Optimisé pour l'utilisation sur GPU
   - Batch size plus grand
   - Nombre d'époques plus élevé
   - Utilisation de CUDA


## Licence

MIT
