import io
import os

import mlflow
import numpy as np
import torch
from fastapi import FastAPI, File, UploadFile
from PIL import Image
from torchvision import transforms


# --------------------------------------------------
# MLflow setup
# --------------------------------------------------
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000"
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


# --------------------------------------------------
# FastAPI app
# --------------------------------------------------
app = FastAPI(
    title="Food11 Model API"
)


# --------------------------------------------------
# Food-11 class names
# ImageFolder uses alphabetical order
# --------------------------------------------------
CLASS_NAMES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit"
]


# --------------------------------------------------
# Image preprocessing
# Same normalization used during training
# --------------------------------------------------
transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------------------------------
# Load model ONCE when API starts
# --------------------------------------------------
MODEL_URI = "models:/food11@champion"

model = mlflow.pyfunc.load_model(
    MODEL_URI
)


# --------------------------------------------------
# Health endpoint
# --------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# --------------------------------------------------
# Prediction endpoint
# --------------------------------------------------
@app.post("/predict")
async def predict(
    file: UploadFile = File(...)
):

    # Read uploaded image
    image_bytes = await file.read()

    image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")


    # Apply same preprocessing as training
    image_tensor = transform(image)

    # Add batch dimension:
    # [3, 128, 128] -> [1, 3, 128, 128]
    image_tensor = image_tensor.unsqueeze(0)


    # MLflow pyfunc expects numpy input
    model_input = image_tensor.numpy()


    # Run prediction
    predictions = model.predict(
        model_input
    )


    # Convert result to PyTorch tensor
    logits = torch.tensor(
        np.asarray(predictions)
    )


    # Convert logits to probabilities
    probabilities = torch.softmax(
        logits,
        dim=1
    )


    # Get most likely class
    confidence, predicted_index = torch.max(
        probabilities,
        dim=1
    )


    predicted_class = CLASS_NAMES[
        predicted_index.item()
    ]


    return {
        "category": predicted_class,
        "confidence": round(
            confidence.item(),
            4
        )
    }
