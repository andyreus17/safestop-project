from flask import render_template, request, jsonify, Response
from app import app, IA_SERVER, IA_URL
import json, requests, os
from utils import *

# Al cargar la pagina cargamos todo
print("Se ha iniciado el servidor Front de Safestop")
load_feed_data()

@app.route("/safestop/front/")
def index():
    feedData = get_feed_data()
    return render_template("index.html", feedData=feedData)

# Cargamos el feed sin procesar ni hacer llamada al modelo
@app.route("/safestop/front/feed<int:num>")
def feed(num):
    return render_template("feed.html", id=num, start="15:50")

# Luego tendremos una llamara para cargar el video y hacer la llamada al modelo
@app.route("/safestop/front/api/feed<int:num>")
def api_feed(num):

    num = str(num)
    # Se carga el feed desde el archivo JSON
    feedData = get_feed_data()

    # Manejamos el caso en que no se encuentra el video
    if num not in feedData:
        return {'error': 'El video no existe'}, 404

    # Manejamos el caso en el modelo ya se ejecuto anteriormente
    # Eso maneja el caso del feed hardcodeado
    if feedData[num]['frames']:
        return feedData[num]

    # Se obtiene la ruta del video
    filename = feedData[num]['name']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'video', filename)

    try:
        # Se llama al modelo
        with open(filepath, 'rb') as video:
            files = {'file': video}
            data = {'name': feedData[num]['name']}
            headers = {'Authorization': "Bearer R2J4cmEgZnJwZXJnYiBjZWJscnBnYiBWTg"}
            apicall = requests.post(IA_SERVER + IA_URL, files=files, data=data, headers=headers)

        if apicall.status_code != 200:
            return {'error': 'Error de la APIcall: {}'.format(apicall.content)}, 500

        # Guardamos los resultados del modelo en el feedData
        api_json = json.loads(apicall.content.decode('utf-8'))
        feedData[num]['frames'] = api_json

        # Guardamos el nuevo feedData en el archivo JSON y cargamos la pagina
        save_feed_data(feedData)
        return feedData[num]

    except Exception as e:
        return {'error': 'Error de una excepcion en front: {}'.format(e)}, 500

# Ahora tendremos una ruta para subir imagenes a static
@app.route("/safestop/front/upload-image", methods=['POST'])
def upload_image():
    # Primero verificamos que la request tenga el token de autenticación
    secret_code = request.headers.get('Authorization', '')
    code = secret_code.replace("Bearer ", "")
    if code != "R2J4cmEgZnJwZXJnYiBjZWJscnBnYiBWTg":
        return jsonify({'error': 'Token de autenticación inválido'}), 403
    
    # Si pasa la verificación, procedemos a guardar la imagen
    image = request.files['image']
    image_name = request.form['name']
    if not image:
        return jsonify({"error": "No file provided"}), 400
    
    # Guardamos la imagen en el directorio static
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'img', image_name)
    image.save(image_path)

    return Response(status=200)

if __name__ == "__main__":
    # Al cargar la aplicación, se cargan los videos
    app.run(port=9001)
