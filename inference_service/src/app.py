import os
import time

from fastapi import FastAPI

from src.controllers.caption_controller import ImageCaptionController
from src.controllers.classifier_controller import ImageClassificationController
from src.dtos import ImageUrl, ClassificationResponse, CaptionResponse

app = FastAPI()

MODEL_URL = os.getenv("MODEL_URL")
LABELS_URL = os.getenv("LABELS_URL")
api_key = os.getenv("OPENAI_API_KEY")


image_classification_service = ImageClassificationController(model_url=MODEL_URL, labels_url=LABELS_URL)
image_caption_service = ImageCaptionController(api_key)


@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}


@app.post("/classify", response_model=ClassificationResponse)
def classify_image(request: ImageUrl):
    start_time = time.perf_counter()  # TODO: use wrapper function
    results = image_classification_service.classify_image(request.image_url)
    end_time = time.perf_counter()
    inference_time_ms = (end_time - start_time) * 1000.0

    return ClassificationResponse(results=results, inference_time_ms=inference_time_ms)


@app.post("/caption", response_model=CaptionResponse)
def caption_image(request: ImageUrl):
    start_time = time.perf_counter()
    caption = image_caption_service.get_caption_for_image(request.image_url)
    end_time = time.perf_counter()
    inference_time_ms = (end_time - start_time) * 1000.0

    return CaptionResponse(caption=caption, inference_time_ms=inference_time_ms)
