import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Load the trained model once when the application starts
MODEL_PATH = os.path.join(os.path.dirname(__file__), "plant_model.keras")
model = load_model(MODEL_PATH)

# Update this list with all your trained classes
class_names = [
    "Apple___Black_rot",
    "Apple___healthy"
]


def predict(img_path):
    try:
        # Load and preprocess image
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0

        # Make prediction
        prediction = model.predict(img_array, verbose=0)

        predicted_index = np.argmax(prediction)
        confidence = float(prediction[0][predicted_index]) * 100

        return {
            "prediction": class_names[predicted_index],
            "confidence": round(confidence, 2)
        }

    except Exception as e:
        raise Exception(f"Error during prediction: {str(e)}")