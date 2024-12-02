import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

from app.modelos import ImagenMascota

# Cargar el modelo Laplacian
model = tf.keras.models.load_model('path_to_your_model/laplacian.h5')

def preprocess_image(image_bytes):
    from PIL import Image
    import numpy as np
    from tensorflow.keras.preprocessing.image import img_to_array

    # Leer imagen desde bytes
    image = Image.open(io.BytesIO(image_bytes)).convert("L").resize((96, 96))  # Escalar a 96x96 en escala de grises
    image_array = img_to_array(image)
    return image_array


def get_images_from_db(db):
    return [record.image_data for record in db.query(ImagenMascota).all()]

def get_labels_from_db(db):
    return [record.label for record in db.query(ImagenMascota).all()]
