from fastapi import FastAPI, File, UploadFile, HTTPException
from model import predict
import shutil
import os

app = FastAPI(
    title="Plant Disease Detection API",
    description="Upload a plant leaf image and get the predicted disease along with confidence.",
    version="1.0.0"
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@app.post(
    "/predict",
    summary="Predict Plant Disease",
    description="Upload a JPG, JPEG or PNG image of a plant leaf to get the predicted disease and confidence score.",
    tags=["Prediction"]
)
async def predict_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG and PNG files are allowed."
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = predict(file_path)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)