import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Load trained model
model = load_model(os.path.join(os.path.dirname(__file__), "plant_model.keras"))

# Class names (IMPORTANT)
class_names = ["Apple___Black_rot", "Apple___healthy"]

def predict(img_path):
    # Load image
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    # Predict
    prediction = model.predict(img_array, verbose=0)

    print("Raw prediction:", prediction)

    index = np.argmax(prediction)

    print("Predicted index:", index)
    print("Predicted class:", class_names[index])

    return class_names[index]
