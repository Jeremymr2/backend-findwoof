import json

from app.segmentation import get_image_from_bytes, get_yolov5_1, get_yolov5_2
from fastapi import UploadFile
import io
from PIL import Image

# Cargar el modelo YOLOv5
model1 = get_yolov5_1()
model2 = get_yolov5_2()

# Función para procesar la imagen, detectar narices y dibujar las cajas
def detect_nose_to_json(binary_image:bytes):
    input_image = get_image_from_bytes(binary_image)
    results = model1(input_image)
    df = results.pandas().xyxy[0]
    if df.empty:
        results = model2(input_image)
    detect_res = results.pandas().xyxy[0].to_json(orient="records")  # JSON img1 predictions
    detect_res = json.loads(detect_res)
    return detect_res

def detect_nose_to_image(binary_image:bytes):
    input_image = get_image_from_bytes(binary_image)
    results = model1(input_image)
    df = results.pandas().xyxy[0]
    if df.empty:
        results = model2(input_image)
    results.render()  # updates results.ims with boxes and labels
    for img in results.ims:
        bytes_io = io.BytesIO()
        img_base64 = Image.fromarray(img)
        img_base64.save(bytes_io, format="jpeg")
    return bytes_io