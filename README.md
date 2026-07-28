#  SafeStop

**SafeStop** es una aplicación web que permite procesar videos para detectar vehículos y reconocer sus patentes utilizando modelos de inteligencia artificial. La aplicación permite cargar videos, analizarlos y presentar los resultados en una tabla con imágenes y datos relevantes como fecha, hora y patente detectada.

##  ¿Qué hace?

- Recibe videos a través de una interfaz web.
- Utiliza un modelo YOLO entrenado para detectar patentes de autos.
- Reconoce el texto de las patentes con OCR (EasyOCR).
- Muestra los resultados en una tabla con:
  - Fecha y hora de detección.
  - Imagen del frame detectado.
  - Patente identificada.
- Permite saltar a un momento específico del video desde la tabla.

##  Estructura del proyecto

```plaintext
safestop/
├── Front/              # Frontend en Flask + HTML + JS
│   └── main.py
│   └── static/
├── IA/                 # Backend con modelo YOLO y OCR
│   └── main/           # Función para procesar video y detectar patentes
```

##  Seguridad

El frontend se comunica con el backend IA mediante un token secreto (secret_code) enviado en el header para evitar llamadas externas no autorizadas.

##  Tecnologías usadas

- Python
- Flask
- JavaScript
- HTML/CSS
- Ultralytics YOLOv8
- EasyOCR

## Notas

- Requiere Python 3.11 (Todo se probo con esa version, puede que funcione con versiones distintas).
- Se recomienda usar GPU si está disponible (aunque funciona en CPU).