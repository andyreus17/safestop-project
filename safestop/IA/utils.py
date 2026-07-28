# -*- coding: utf-8 -*-
from app import IA_URL, IA_SERVER
from datetime import datetime
import os
import re
from zoneinfo import ZoneInfo
import requests
import threading
import io

import cv2

from app import model, reader, STATIC_FOLDER

ZONE = ZoneInfo("America/Santiago")
CONFIDENCE_THRESHOLD = 0.1
ASPECT_RATIO_RANGE = (2.0, 4.0)
TRACKER_CONFIG_PATH = 'custom_botsort.yaml'
P = 2

def upload_image_to_front(archivo, nombre):
    try:
        # La imagen es de tipo ndarray y la pasaremos a bytes
        success, buffer = cv2.imencode('.png', archivo)
        if not success:
            raise Exception("Error al codificar la imagen a PNG")

        file = io.BytesIO(buffer.tobytes())
        file.name = nombre 
        # Luego subimos la imagen al servidor
        files = {'image': file}
        data = {'name': nombre}
        headers = {'Authorization': "Bearer R2J4cmEgZnJwZXJnYiBjZWJscnBnYiBWTg"}
        request = requests.post(IA_SERVER + IA_URL, files=files, data=data, headers=headers)
        
        if request.status_code != 200:
            print(f"Error al subir la imagen: {request.status_code} - {request.text}")
            raise Exception(f"Error al subir la imagen: {request.status_code} - {request.text}")
        
    except Exception as e:
        print(f"[ERROR] Subida async fallida: {e}")
        
def platesOCR(img, id):
    # redimensionar la imagen
    scale_factor = 5
    img_resized = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

    # convertir imagen a escala de grises
    img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

    # OCR
    results = reader.recognize(img_gray, adjust_contrast=0.0)

    if not results:
        return ('No text', 0)
    else:
        print(f"Resultados de OCR para id {id}:")
        print(results[0][1])
        return (results[0][1], results[0][2])

def es_patente_valida(patente):
    """Verifica si la patente cumple con los formatos permitidos: LLLLNN, LLNNNN o con espacios."""
    patente = patente.upper()
    formato1 = re.compile(r'^[A-Z]{4}[0-9]{2}$')  # LLLLNN
    formato2 = re.compile(r'^[A-Z]{2}[0-9]{4}$')  # LLNNNN
    formato3 = re.compile(r'^[A-Z]{2} [A-Z]{2} [0-9]{2}$')  # LL LL NN
    formato4 = re.compile(r'^[A-Z]{2} [0-9]{2} [0-9]{2}$')  # LL NN NN
    return formato1.match(patente) or formato2.match(patente) or formato3.match(patente) or formato4.match(patente)

def lector_patentes(video_path, video_name):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: No se pudo abrir el archivo de video {video_path}")
        exit()

    # Estructura para almacenar los resultados
    best_detections = {}
    invalid_tracks = []
    frame_count = 0

    # Inicializar el modelo de detección
    FRAME_SKIP = 1
    while cap.isOpened():
        for _ in range(FRAME_SKIP):
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
        if not ret:
            break

        # Mostrar el progreso
        if frame_count % 10 == 0:
            print(f"Procesando frame {frame_count}")

        # Realizar la detección de objetos
        try:
            results = model.track(source=frame,
                                    conf=CONFIDENCE_THRESHOLD,
                                    save=False,
                                    verbose=False,
                                    imgsz=640,
                                    tracker=TRACKER_CONFIG_PATH,
                                    persist=True,
                                    stream=False)
        except Exception as e:
            print(f"Error al procesar el frame {frame_count}: {e}")
            continue

        # Procesar los resultados
        boxes = results[0].boxes
        if hasattr(boxes, 'id') and boxes.id is not None:
            ids = boxes.id.int()
            confs = boxes.conf
            xyxy = boxes.xyxy

            for i in range(len(ids)):
                track_id = int(ids[i].item())
                conf = float(confs[i].item())
                bbox = xyxy[i].tolist()
                x1, y1, x2, y2 = map(int, bbox)
                width = x2 - x1
                height = y2 - y1
                aspect_ratio = width / height
                area = width * height

                # Filtrar detecciones según restricciones
                if not (ASPECT_RATIO_RANGE[0] <= aspect_ratio <= ASPECT_RATIO_RANGE[1]):
                    continue

                # Calcular puntaje de calidad
                score = area * (conf ** P)

                # Guardar la mejor detección
                if track_id not in best_detections or score > best_detections[track_id]['score']:
                    plate_crop = frame[y1:y2, x1:x2]
                    now = datetime.now(ZONE)
                    date = now.strftime("%d/%m/%Y")
                    time = now.strftime("%H:%M")
                    
                    best_detections[int(track_id)] = {
                        'score': score,
                        'date': date,
                        'time': time,
                        'plate_crop': plate_crop,
                        'frame': frame
                    }
                    print("Se detecto una posible patente:")
                    print(f"Mejor detección para track_id {track_id}: score={score}, date={date}, time={time}")
    cap.release()

    # Guardar los resultados
    for track_id, detection in best_detections.items():
        plate_crop = detection['plate_crop']
        frame = detection['frame']
        patent, conf = platesOCR(plate_crop, track_id)

        # Se verifica que la patente tenga formato válido
        if not es_patente_valida(patent):
            print(f"Patente descartada por formato inválido: {patent}")
            invalid_tracks.append(track_id)
            continue

        # Guardamos las imágenes en el servidor
        threading.Thread(target=upload_image_to_front, args=(plate_crop, f"{video_name}_plate_{track_id}.png")).start()
        threading.Thread(target=upload_image_to_front, args=(frame, f"{video_name}_frame_{track_id}.png")).start()

        # Change the value of plate_crop to the path of the saved image
        best_detections[track_id]['plate_crop'] = os.path.join(STATIC_FOLDER, "img", f"{video_name}_plate_{track_id}.png")
        best_detections[track_id]['frame'] = os.path.join(STATIC_FOLDER, "img", f"{video_name}_frame_{track_id}.png")
        best_detections[track_id]['patent'] = patent

    # Devolver el diccionario con los resultados, descartando las detecciones inválidas
    for track_id in invalid_tracks:
        del best_detections[track_id]

    return best_detections
