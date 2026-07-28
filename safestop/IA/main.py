#-*- coding: utf-8 -*-
from app import app
from utils import lector_patentes
from flask import request, jsonify
import tempfile

print("Se ha iniciado el servidor IA de Safestop")

@app.route('/safestop/ia/predict', methods=['POST'])
def predict():
    print("Se ha recibido una petición de predicción")
    
    # Revisamos si el codigo secreto es correcto
    secret_code = request.headers.get('Authorization', '')
    code = secret_code.replace("Bearer ", "")
    if code != "R2J4cmEgZnJwZXJnYiBjZWJscnBnYiBWTg":
        return jsonify({'error': 'Token de autenticación inválido'}), 403

    # El video se recibe como un archivo
    video_file = request.files['file']
    video_name = request.form['name']
    if not video_file:
        return jsonify({"error": "No file provided"}), 400

    # Guardar video temporalmente en disco
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        video_file.save(tmp)
        tmp_path = tmp.name

    # Procesar el video
    try:
        best_detections = lector_patentes(tmp_path, video_name)
    except Exception as e:
        print("Excepción al procesar el video:", e)
        return jsonify({"error": f"Error al procesar el video"}), 500

    return jsonify(best_detections)

if __name__ == '__main__':
    app.run(port=9002)