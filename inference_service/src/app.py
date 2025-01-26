import os
import time

from fastapi import FastAPI

from src.controller import ImageClassificationController
from src.dtos import ClassificationRequest, ClassificationResponse

app = FastAPI()
# TODO: move to environment variables
os.environ["TFHUB_CACHE_DIR"] = "/app/model_cache"
MODEL_URL = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4"
LABELS_URL = "https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt"

image_classification_service = ImageClassificationController(model_url=MODEL_URL, labels_url=LABELS_URL)
"""
# TODO: use dependency injection
"""


@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}

@app.post("/classify", response_model=ClassificationResponse)
def classify_image(request: ClassificationRequest):

    start_time = time.perf_counter()
    results = image_classification_service.classify_image(request.image_url)
    end_time = time.perf_counter()
    inference_time_ms = (end_time - start_time) * 1000.0

    return ClassificationResponse(
        results=results,
        inference_time_ms=inference_time_ms
    )
