import tensorflow as tf
from fastapi import FastAPI, File, UploadFile
import numpy as np
from PIL import Image
import io

app = FastAPI()

# Load your model (assuming you saved it as 'plant_model.h5')
model = tf.keras.models.load_model('plant_model.h5')
class_names = ['Apple___healthy', 'Corn___unhealthy', 'Potato___healthy'] # Add all your classes

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read and preprocess the image
    image_data = await file.read()
    img = Image.open(io.BytesIO(image_data)).resize((224, 224))
    img_array = np.expand_dims(tf.keras.preprocessing.image.img_to_array(img) / 255.0, axis=0)
    
    # Predict
    prediction = model.predict(img_array)
    result = class_names[np.argmax(prediction)]
    return {"prediction": result}