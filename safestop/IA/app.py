# -*- coding: utf-8 -*-
from flask import Flask
from ultralytics import YOLO
import easyocr
import torch
import os

# Como el static esta en el front, usaremos la ruta del front
IA_SERVER = 'http://gate.dcc.uchile.cl:8632'
# IA_SERVER = 'http://localhost:9001'

IA_URL = '/safestop/front/upload-image'

STATIC_FOLDER = "/front/static"

app = Flask(__name__)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024 # 200MB limites

model = YOLO('best_nano_medium.pt')
reader = easyocr.Reader(lang_list=['en'], 
                        gpu=True, 
                        model_storage_directory=os.path.expanduser('~/proyectoIA/safestop-project/safestop/IA/EasyOCR/model'), 
                        user_network_directory=os.path.expanduser('~/proyectoIA/safestop-project/safestop/IA/EasyOCR/user_network'), 
                        recog_network='custom_model', 
                        detector=False, 
                        recognizer=True
)

print("GPU disponible:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Nombre de GPU:", torch.cuda.get_device_name(0))

if torch.cuda.is_available():
    model.to('cuda')
    print("YOLO cargado en GPU")
else:
    print("YOLO usando CPU")