import os
import json
from app import app

# Funcion para obtener todos los videos de la carpeta static/video
# Se guardar en un archivo JSON en formato de diccionario
def load_feed_data():
    # Leeremos el contenido de la carpeta static/video
    videos = os.listdir(app.config['UPLOAD_FOLDER'] + 'video/')
    videos = sorted(videos)  # Ordenamos los videos alfabéticamente

    # Luego crearemos el diccionario de videos
    feedData = {}
    for idx, video in enumerate(videos, start=1):
        if video == "video1.mp4":
            feedData[idx] = {'name': video, "frames": {
                                                        "1": {
                                                            "date": "21/4/25",
                                                            "frame": "/front/static/img/video1foto1.png",
                                                            "plate_crop": "/front/static/img/video1frame1.png",
                                                            "time": "15:52",
                                                            "patent": "SJJV86"
                                                        },
                                                        "2": {
                                                            "date": "21/4/25",
                                                            "frame": "/front/static/img/video1foto2.png",
                                                            "plate_crop": "/front/static/img/video1frame2.png",
                                                            "time": "16:11",
                                                            "patent": "KDDG45"
                                                        },
                                                        "3": {
                                                            "date": "21/4/25",
                                                            "frame": "/front/static/img/video1foto3.png",
                                                            "plate_crop": "/front/static/img/video1frame3.png",
                                                            "time": "16:30",
                                                            "patent": "JFTJ49"
                                                        }
                                                      }}
        else:
            feedData[idx] = {'name': video, 'frames': {}}
    
    # Y finalmente, vaciamos los archivos generados anteriormente
    files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'img'))
    hardcoded_files = ["calle.png", "feed.jpg", "video1foto1.png", "video1foto2.png", "video1foto3.png", "video1frame1.png", "video1frame2.png", "video1frame3.png"]
    for file in files:
        if file not in hardcoded_files:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'img', file))
    
    # Guardamos el diccionario en un archivo JSON
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'data', 'feed.json'), 'w') as outfile:
        json.dump(feedData, outfile, indent=4)
        
# Funcion para obtener el feed de videos desde el archivo JSON
def get_feed_data():
    # Cargamos el feed desde el archivo JSON
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'data', 'feed.json'), 'r') as outfile:
        feedData = json.load(outfile)
    return feedData

# Funcion para guardar el nuevo feedData en el archivo JSON
def save_feed_data(feedData):
    # Guardamos el diccionario en un archivo JSON
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'data', 'feed.json'), 'w') as outfile:
        json.dump(feedData, outfile, indent=4)