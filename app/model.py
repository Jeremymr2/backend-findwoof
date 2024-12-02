
def predict(image_input):
    img = Image.open(image_input)
    img = img.resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.array([img_array]) 
    
    # generate predictions for samples
    predictions = resnet101_model.predict(img_array)
    print(predictions)

    # generate argmax for predictions
    class_id = np.argmax(predictions, axis = 1)
    print(class_id)

    # transform classes number into classes name
    return class_names[class_id.item()]