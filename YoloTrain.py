from ultralytics import YOLO
import argparse

def train_csgo_detector(use_server_config):
    model = YOLO('yolo11n.pt')

    if use_server_config:
        #GPU
        train_args = {
            'data': 'data.yaml',
            'epochs': 500,
            'imgsz': 640,
            'batch': 128,  
            'patience': 15,
            'save': True,
            'device': 'cuda',  
            'save_period': 30,
            'workers': 8,  
            'optimizer': 'Adam',  
            'lr0': 0.0001,
            'weight_decay': 0.0005,
            'momentum': 0.937,
            'project': 'runs/detect',
            'name': 'duo_classes_server',
            'exist_ok': True,
            'verbose': True
        }
    else:
        #CPU
        train_args = {
            'data': 'data.yaml',
            'epochs': 100,
            'imgsz': 640,
            'batch': 16,  
            'patience': 5,
            'save': True,
            'device': 'cpu', 
            'save_period': 10,
            'workers': 12,  
            'optimizer': 'SGD',  
            'lr0': 0.01,
            'weight_decay': 0.0005,
            'momentum': 0.937,
            'project': 'runs/detect',
            'name': 'duo_classes_local',
            'exist_ok': True,
            'verbose': True
        }

    results = model.train(**train_args)
    
    return model, results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a CSGO detector with YOLO.")
    parser.add_argument('--use_server', type=bool, default=False,
                        help='Set to True to use server configuration with GPU, False for local CPU configuration.')
    
    args = parser.parse_args()
    
    model, results = train_csgo_detector(args.use_server)
    model.save('csgo_detector.pt')