import json

from segmentation import get_image_from_bytes, get_yolov5
from fastapi import UploadFile
import io
from PIL import Image

# Cargar el modelo YOLOv5
model = get_yolov5()

# Función para procesar la imagen, detectar narices y dibujar las cajas
def detect_nose_to_json(binary_image:bytes):
    input_image = get_image_from_bytes(binary_image)
    results = model(input_image)
    print(results)
    detect_res = results.pandas().xyxy[0].to_json(orient="records")  # JSON img1 predictions
    detect_res = json.loads(detect_res)
    return detect_res

def detect_nose_to_image(binary_image:bytes):
    input_image = get_image_from_bytes(binary_image)
    results = model(input_image)
    results.render()  # updates results.imgs with boxes and labels
    for img in results.ims:
        bytes_io = io.BytesIO()
        img_base64 = Image.fromarray(img)
        img_base64.save(bytes_io, format="jpeg")
    return bytes_io